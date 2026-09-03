# -*- coding: utf-8 -*-

from odoo import models


class CarRepairBilling(models.TransientModel):
    """Container for Car Repair Billing menu / server actions."""

    _name = 'car.repair.billing'
    _description = 'Car Repair Billing'

    def action_billing_invoices(self):
        """Open Customer Invoices list filtered for Car Repair billing."""
        return {
            'name': 'Billing & Invoices',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,kanban,form',
            'domain': [('move_type', '=', 'out_invoice')],
            'context': {'default_move_type': 'out_invoice'},
        }
