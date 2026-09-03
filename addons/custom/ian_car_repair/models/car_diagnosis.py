# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CarDiagnosis(models.Model):
    """Car Diagnosis: stores the diagnostic result and spare parts needed."""

    _name = 'car.diagnosis'
    _description = 'Car Diagnosis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Diagnosis Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: self._get_default_name(),
    )
    repair_order_id = fields.Many2one(
        'car.repair.order',
        string='Repair Order',
        required=True,
        ondelete='cascade',
        tracking=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        related='repair_order_id.partner_id',
        store=True,
        readonly=True,
    )
    technician_id = fields.Many2one(
        'res.users',
        string='Technician',
        tracking=True,
    )
    diagnostic_result = fields.Html(
        string='Diagnostic Result',
        tracking=True,
    )
    estimated_hours = fields.Float(string='Estimated Hours')
    service_product_id = fields.Many2one(
        'product.product',
        string='Service Product',
        domain="[('type', '=', 'service')]",
    )
    spare_part_ids = fields.One2many(
        'car.diagnosis.spare.part',
        'diagnosis_id',
        string='Spare Parts',
    )

    state = fields.Selection(
        [
            ('draft', 'DRAFT'),
            ('in_progress', 'IN DIAGNOSIS'),
            ('complete', 'COMPLETE'),
        ],
        string='Status',
        default='draft',
        tracking=True,
        copy=False,
    )

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('car.diagnosis') or 'New'

    def action_start(self):
        """Start diagnosis: set state to IN DIAGNOSIS."""
        for record in self:
            record.write({'state': 'in_progress'})

    def action_complete(self):
        """Mark diagnosis as COMPLETE."""
        for record in self:
            record.write({'state': 'complete'})

    def action_create_quotation(self):
        """Create a sale.order (quotation) from the diagnosis line items.

        Service product + spare parts become sale order lines.
        """
        self.ensure_one()
        if self.state != 'complete':
            raise ValueError(
                "Diagnosis must be COMPLETE before creating a quotation."
            )

        sale_order_obj = self.env['sale.order']
        lines = []

        # Service product line
        if self.service_product_id:
            lines.append((0, 0, {
                'product_id': self.service_product_id.id,
                'product_uom_qty': self.estimated_hours or 1.0,
                'name': self.service_product_id.name,
            }))

        # Spare parts lines
        for part in self.spare_part_ids:
            lines.append((0, 0, {
                'product_id': part.product_id.id,
                'product_uom_qty': part.quantity,
                'price_unit': part.unit_price,
                'name': part.product_id.name,
            }))

        sale_order = sale_order_obj.create({
            'partner_id': self.partner_id.id,
            'order_line': lines,
        })

        # Link the sale order back to this diagnosis
        sale_order.write({
            'car_diagnosis_id': self.id,
        })

        return {
            'name': 'Quotation',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }


class CarDiagnosisSparePart(models.Model):
    """Spare part line inside a Car Diagnosis."""

    _name = 'car.diagnosis.spare.part'
    _description = 'Car Diagnosis Spare Part'

    diagnosis_id = fields.Many2one(
        'car.diagnosis',
        string='Diagnosis',
        ondelete='cascade',
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain="[('type', '=', 'consu')]",
    )
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    unit_price = fields.Float(string='Unit Price')
