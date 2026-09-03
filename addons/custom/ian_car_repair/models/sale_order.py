# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    """Extension of sale.order to integrate with Car Repair workflow."""

    _inherit = 'sale.order'

    car_diagnosis_id = fields.Many2one(
        'car.diagnosis',
        string='Car Diagnosis',
        ondelete='set null',
    )
    car_work_order_id = fields.Many2one(
        'car.work.order',
        string='Car Work Order',
        ondelete='set null',
    )
    car_repair_order_id = fields.Many2one(
        'car.repair.order',
        string='Car Repair Order',
        ondelete='set null',
    )

    def action_confirm(self):
        """On confirmation, create the corresponding Car Work Order and set
        the linked Repair Order to WORK IN PROGRESS."""
        result = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.car_diagnosis_id:
                diagnosis = order.car_diagnosis_id
                work_order = self.env['car.work.order'].create({
                    'sale_order_id': order.id,
                    'repair_order_id': diagnosis.repair_order_id.id,
                    'diagnosis_id': diagnosis.id,
                    'technician_id': diagnosis.technician_id.id,
                })
                order.write({'car_work_order_id': work_order.id})
                if diagnosis.repair_order_id:
                    diagnosis.repair_order_id.action_to_progress()
        return result

    def action_create_work_order_invoice(self):
        """Generate an invoice from the work order: service hours + spare parts.

        This reuses the standard sale invoice mechanism so amounts, taxes and
        accounts follow the configured sale order.
        """
        self.ensure_one()
        if not self.car_work_order_id:
            raise ValueError(
                "No Car Work Order linked to this sale order."
            )
        work_order = self.car_work_order_id
        if work_order.state != 'finished':
            raise ValueError(
                "Work Order must be FINISHED before generating an invoice."
            )
        # Use the standard sale order invoice action
        return {
            'name': 'Create Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'active_id': self.id,
                'active_ids': [self.id],
            },
        }
