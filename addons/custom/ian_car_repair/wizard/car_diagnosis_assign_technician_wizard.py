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
        """Write technician to the repair order, change state, and propagate
        the technician to all linked car.diagnosis records."""
        self.ensure_one()
        repair_order = self.repair_order_id

        # Write technician only (do not force state; diagnosis/quotation
        # flow advances the state via its own buttons)
        repair_order.write({
            'assigned_id': self.technician_id.id,
        })

        # Propagate technician to all linked diagnoses
        if repair_order.diagnosis_ids:
            repair_order.diagnosis_ids.write({
                'technician_id': self.technician_id.id,
            })

        return {'type': 'ir.actions.act_window_close'}
