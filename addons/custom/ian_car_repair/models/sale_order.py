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
                })
                order.write({'car_work_order_id': work_order.id})
                if diagnosis.repair_order_id:
                    diagnosis.repair_order_id.action_to_progress()
        return result

    def action_create_work_order_invoice(self):
        """Generate a customer invoice from the confirmed Sale Order.

        Uses Odoo's standard ``_create_invoices()`` method so that all line
        items (service hours + spare parts), taxes and accounts are derived
        from the configured Sale Order.  The resulting ``account.move`` is
        returned to the user in a form view.

        Raises:
            ValueError: If no linked Work Order exists or it is not finished.
        """
        self.ensure_one()

        if not self.car_work_order_id:
            raise ValueError(
                "No Car Work Order linked to this sale order."
            )
        if self.car_work_order_id.state != 'finished':
            raise ValueError(
                "Work Order must be FINISHED before generating an invoice."
            )
        if self.invoice_ids.filtered(
            lambda inv: inv.move_type == 'out_invoice'
                        and inv.state != 'cancel'
        ):
            raise ValueError(
                "An open Customer Invoice already exists for this Sale Order."
            )

        # Use Odoo's built-in method to create the invoice from the SO lines.
        # ``_create_invoices()`` respects pricelists, taxes and fiscal positions
        # configured on the Sale Order.
        invoices = self._create_invoices()

        if not invoices:
            raise ValueError(
                "No invoice was generated. Please verify the Sale Order lines."
            )

        # Return the first customer invoice (out_invoice) to the user.
        invoice = invoices.filtered(
            lambda inv: inv.move_type == 'out_invoice'
        )[:1]

        return {
            'name': 'Customer Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }
