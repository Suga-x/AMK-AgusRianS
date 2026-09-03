# -*- coding: utf-8 -*-

from odoo import fields, models


class CarRepairChecklist(models.Model):
    """Master data of checklists used in Car Repair Orders."""

    _name = 'car.repair.checklist'
    _description = 'Car Repair Checklist'
    _order = 'name'

    name = fields.Char(string='Checklist Name', required=True)
    created_by_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True,
    )
