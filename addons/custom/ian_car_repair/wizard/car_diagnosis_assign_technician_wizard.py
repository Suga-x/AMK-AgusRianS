# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CarDiagnosisAssignTechnicianWizard(models.TransientModel):
    """Wizard to assign a technician to a car repair order and its diagnoses."""

    _name = 'car.diagnosis.assign.technician.wizard'
    _description = 'Assign Technician to Repair Order'

    repair_order_id = fields.Many2one(
        'car.repair.order',
        string='Repair Order',
        required=True,
    )
    technician_id = fields.Many2one(
        'res.users',
        string='Technician',
        required=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            res['repair_order_id'] = active_id
        return res

    def action_assign(self):
        """Assign a technician to the repair order.

        The technician is stored on ``car.repair.order.assigned_id`` and is
        automatically propagated to all linked diagnoses and work orders via
        their related ``technician_id`` fields.
        """
        self.ensure_one()
        self.repair_order_id.write({
            'assigned_id': self.technician_id.id,
        })
        return {'type': 'ir.actions.act_window_close'}
