# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CarWorkOrder(models.Model):
    """Car Work Order: tracks execution of a job by a technician."""

    _name = 'car.work.order'
    _description = 'Car Work Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Work Order Reference',
        copy=False,
        readonly=True,
        index=True,
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        ondelete='set null',
    )
    repair_order_id = fields.Many2one(
        'car.repair.order',
        string='Repair Order',
        ondelete='set null',
    )
    diagnosis_id = fields.Many2one(
        'car.diagnosis',
        string='Diagnosis',
        ondelete='set null',
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
        related='repair_order_id.assigned_id',
        store=True,
        readonly=True,
        tracking=True,
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        tracking=True,
    )
    duration_hours = fields.Float(string='Duration (Hours)', readonly=True)
    priority = fields.Selection(
        [('0', 'Low'), ('1', 'Medium'), ('2', 'High'), ('3', 'Very High')],
        string='Priority',
        default='1',
        tracking=True,
    )

    state = fields.Selection(
        [
            ('draft', 'DRAFT'),
            ('in_progress', 'IN PROGRESS'),
            ('pending', 'PENDING'),
            ('finished', 'FINISHED'),
            ('cancel', 'CANCELLED'),
        ],
        string='Status',
        default='draft',
        tracking=True,
        copy=False,
    )

    # --- Elapsed hours tracking (internal) ---
    date_start = fields.Datetime(string='Start Date', readonly=True)
    date_end = fields.Datetime(string='End Date', readonly=True)

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('car.work.order') or 'New'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self._get_default_name()
        return super().create(vals_list)

    def action_start(self):
        """Start execution of the work order."""
        now = fields.Datetime.now()
        for record in self:
            record.write({
                'state': 'in_progress',
                'date_start': now,
            })

    def action_pause(self):
        """Pause execution (goes to PENDING) and aggregate elapsed time."""
        now = fields.Datetime.now()
        for record in self:
            elapsed = record._compute_period_hours(record.date_start, now)
            record.write({
                'state': 'pending',
                'duration_hours': record.duration_hours + elapsed,
            })

    def action_pending(self):
        """Alias of action_pause (state -> pending)."""
        self.action_pause()

    def action_resume(self):
        """Resume execution from PENDING to IN PROGRESS."""
        now = fields.Datetime.now()
        for record in self:
            record.write({
                'state': 'in_progress',
                'date_start': now,
            })

    def action_finish(self):
        """Finish the work order and store accumulated elapsed hours."""
        now = fields.Datetime.now()
        for record in self:
            elapsed = record._compute_period_hours(record.date_start, now)
            total_hours = record.duration_hours + elapsed
            record.write({
                'state': 'finished',
                'date_end': now,
                'duration_hours': total_hours,
            })
            if record.repair_order_id:
                record.repair_order_id.action_to_done()

    def action_cancel(self):
        """Cancel the work order."""
        for record in self:
            record.write({'state': 'cancel'})

    @staticmethod
    def _compute_period_hours(date_start, date_end):
        """Return elapsed hours between two datetimes (0 if invalid)."""
        if not date_start or not date_end:
            return 0.0
        delta = date_end - date_start
        hours = delta.total_seconds() / 3600.0
        return round(hours, 2)
