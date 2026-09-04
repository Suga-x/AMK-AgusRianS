# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CarRepairOrder(models.Model):
    """Car Repair Order, receives a vehicle and its state flow."""

    _name = 'car.repair.order'
    _description = 'Car Repair Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_receipt desc, id desc'

    name = fields.Char(
        string='Order Reference',
        copy=False,
        readonly=True,
        index=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        tracking=True,
    )
    address = fields.Char(string='Address', tracking=True, related="partner_id.street")
    phone = fields.Char(string='Phone', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    # subject = fields.Many2one(
    #     'car.repair.checklist',
    #     string='Subject',
    # )
    subject = fields.Char(string='Subject', tracking=True)
    assigned_id = fields.Many2one(
        'res.users',
        string='Assigned To',
        tracking=True,
    )
    date_receipt = fields.Datetime(
        string='Received Date',
        default=fields.Datetime.now,
        tracking=True,
    )
    priority = fields.Selection(
        [('0', 'Low'), ('1', 'Medium'), ('2', 'High'), ('3', 'Very High')],
        string='Priority',
        default='1',
        tracking=True,
    )
    repair_note = fields.Text(string='Repair Note', tracking=True)

    line_ids = fields.One2many(
        'car.repair.order.line',
        'repair_order_id',
        string='Vehicle Lines',
    )
    checklist_ids = fields.Many2many(
        'car.repair.checklist',
        string='Checklists',
    )
    work_order_ids = fields.One2many(
        'car.work.order',
        'repair_order_id',
        string='Work Orders',
    )
    diagnosis_ids = fields.One2many(
        'car.diagnosis',
        'repair_order_id',
        string='Diagnoses',
    )
    work_order_count = fields.Integer(
        string='Work Order Count',
        compute='_compute_work_order_count',
    )
    diagnosis_count = fields.Integer(
        string='Diagnosis Count',
        compute='_compute_diagnosis_count',
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        ondelete='set null',
    )
    sale_order_count = fields.Integer(
        string='Sale Order Count',
        compute='_compute_sale_order_count',
    )
    is_technician_assigned = fields.Boolean(
        string='Technician Assigned',
        compute='_compute_is_technician_assigned',
    )

    state = fields.Selection(
        [
            ('draft', 'DRAFT'),
            ('in_progress', 'IN PROGRESS'),
            ('done', 'DONE'),
        ],
        string='Status',
        default='draft',
        tracking=True,
        copy=False,
    )

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('car.repair.order') or 'New'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self._get_default_name()
        return super().create(vals_list)

    def action_to_progress(self):
        """Move Repair Order from RECEIVED to IN PROGRESS."""
        for record in self:
            record.write({'state': 'in_progress'})

    def action_to_done(self):
        """Move Repair Order from IN PROGRESS to DONE."""
        for record in self:
            record.write({'state': 'done'})

    @api.depends('work_order_ids')
    def _compute_work_order_count(self):
        for record in self:
            record.work_order_count = len(record.work_order_ids)

    @api.depends('diagnosis_ids')
    def _compute_diagnosis_count(self):
        for record in self:
            record.diagnosis_count = len(record.diagnosis_ids)

    @api.depends('sale_order_id')
    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = 1 if record.sale_order_id else 0

    @api.depends('assigned_id', 'diagnosis_ids.technician_id')
    def _compute_is_technician_assigned(self):
        """Return True when assigned_id is set AND every diagnosis has a technician."""
        for record in self:
            has_assigned = bool(record.assigned_id)
            all_diag_assigned = (
                record.diagnosis_ids
                and all(d.technician_id for d in record.diagnosis_ids)
            )
            record.is_technician_assigned = has_assigned and all_diag_assigned

    def action_view_diagnosis(self):
        """Open the list of diagnoses linked to this repair order."""
        self.ensure_one()
        return {
            'name': 'Car Diagnoses',
            'type': 'ir.actions.act_window',
            'res_model': 'car.diagnosis',
            'view_mode': 'list,form',
            'domain': [('repair_order_id', '=', self.id)],
            'context': {'default_repair_order_id': self.id},
        }

    def action_view_work_orders(self):
        """Open the list of work orders linked to this repair order."""
        self.ensure_one()
        return {
            'name': 'Car Work Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'car.work.order',
            'view_mode': 'list,form',
            'domain': [('repair_order_id', '=', self.id)],
            'context': {'default_repair_order_id': self.id},
        }

    def action_create_work_order(self):
        """Create a work order linked to this repair order."""
        self.ensure_one()
        work_order = self.env['car.work.order'].create({
            'repair_order_id': self.id,
        })
        return {
            'name': 'Car Work Order',
            'type': 'ir.actions.act_window',
            'res_model': 'car.work.order',
            'res_id': work_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_assign_technician(self):
        """Open wizard to assign a technician to this repair order."""
        self.ensure_one()
        return {
            'name': 'Assign Technician',
            'type': 'ir.actions.act_window',
            'res_model': 'car.diagnosis.assign.technician.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }

    def action_create_diagnosis(self):
        """Create a car diagnosis linked to this repair order
        and move vehicle lines to IN DIAGNOSIS."""
        self.ensure_one()
        diagnosis = self.env['car.diagnosis'].create({
            'repair_order_id': self.id,
            'partner_id': self.partner_id.id,
        })
        # Move all vehicle lines to in_diagnosis state
        self.line_ids.write({'state': 'in_diagnosis'})
        # Move repair order to in_progress
        self.write({'state': 'in_progress'})
        return {
            'name': 'Car Diagnosis',
            'type': 'ir.actions.act_window',
            'res_model': 'car.diagnosis',
            'res_id': diagnosis.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_quotation(self):
        """Create a sale.order (quotation) from all linked diagnoses.

        Collects service products and spare parts from every diagnosis
        linked to this repair order and creates a single sale order.
        """
        self.ensure_one()
        sale_order_obj = self.env['sale.order']
        lines = []

        for diagnosis in self.diagnosis_ids:
            # Service product line
            if diagnosis.service_product_id:
                lines.append((0, 0, {
                    'product_id': diagnosis.service_product_id.id,
                    'product_uom_qty': diagnosis.estimated_hours or 1.0,
                    'name': diagnosis.service_product_id.name,
                }))
            # Spare parts lines
            for part in diagnosis.spare_part_ids:
                lines.append((0, 0, {
                    'product_id': part.product_id.id,
                    'product_uom_qty': part.quantity,
                    'price_unit': part.unit_price,
                    'name': part.product_id.name,
                }))

        if not lines:
            raise ValueError(
                "No diagnosis data found. Please complete at least one "
                "diagnosis with a service product or spare parts before "
                "creating a quotation."
            )

        sale_order = sale_order_obj.create({
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'order_line': lines,
            'car_repair_order_id': self.id,
        })

        self.write({
            'sale_order_id': sale_order.id,
        })

        return {
            'name': 'Quotation',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_sale_order(self):
        """Open the linked sale order form."""
        self.ensure_one()
        if not self.sale_order_id:
            return False
        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }


class CarRepairOrderLine(models.Model):
    """Vehicle line inside a Car Repair Order."""

    _name = 'car.repair.order.line'
    _description = 'Car Repair Order Vehicle Line'
    _order = 'id'

    repair_order_id = fields.Many2one(
        'car.repair.order',
        string='Repair Order',
        ondelete='cascade',
        required=True,
    )
    car_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    license_plate = fields.Char(string='License Plate')
    model_id = fields.Many2one('fleet.vehicle.model', string='Model')
    chassis_number = fields.Char(string='Chassis Number')
    fuel_type = fields.Selection(
        [
            ('gasoline', 'Gasoline'),
            ('diesel', 'Diesel'),
            ('electric', 'Electric'),
            ('hybrid', 'Hybrid'),
            ('lpg', 'LPG'),
        ],
        string='Fuel Type',
    )
    under_guarantee = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')],
        string='Under Guarantee',
    )
    guarantee_type = fields.Selection(
        [('paid', 'Paid'), ('free', 'Free')],
        string='Guarantee Type',
    )
    nature_of_service = fields.Char(string='Nature of Service')
    odometer = fields.Float(string='Odometer')

    state = fields.Selection(
        [
            ('draft', 'DRAFT'),
            ('in_diagnosis', 'IN DIAGNOSIS'),
            ('done', 'DONE'),
            ('cancel', 'CANCELLED'),
        ],
        string='Status',
        default='draft',
        tracking=True,
        copy=False,
    )

    def action_enter_result(self):
        """Move from IN DIAGNOSIS to DONE (Enter Result)."""
        for record in self:
            record.write({'state': 'done'})

    def action_cancel(self):
        """Cancel the vehicle line."""
        for record in self:
            record.write({'state': 'cancel'})

    @api.onchange('car_id')
    def _onchange_car_id(self):
        """Auto-fill vehicle details from the selected fleet vehicle."""
        for line in self:
            if line.car_id:
                line.license_plate = line.car_id.license_plate or False
                line.model_id = line.car_id.model_id or False
                line.chassis_number = line.car_id.vin_sn or False
                line.fuel_type = line.car_id.fuel_type or False
                line.odometer = line.car_id.odometer or 0.0
            else:
                line.license_plate = False
                line.model_id = False
                line.chassis_number = False
                line.fuel_type = False
                line.odometer = 0.0
