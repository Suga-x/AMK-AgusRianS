# -*- coding: utf-8 -*-
{
    'name': "Car Repair & Automotive Service Management",
    'summary': "Manage car repair orders, diagnoses, quotations, invoices and work orders",
    'description': """
        Car Repair & Automotive Service Management Application
        =====================================================
        This module implements a complete workflow for car repair and
        automotive service management:
        * Car Repair Checklist master data
        * Car Repair Orders with vehicle lines and checklist selection
        * Car Diagnosis and technician assignment
        * Work Orders with execution flow and elapsed hours tracking
        * Sale Quotation creation from diagnosis and invoice generation
    """,
    'author': "Ian",
    'website': "https://www.example.com",
    'category': 'Services/Car Repair',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'application': True,
    'depends': ['base', 'sale_management', 'account', 'fleet', 'mail'],
    'data': [
        'data/sequences.xml',
        'security/car_repair_security.xml',
        'security/ir.model.access.csv',
        'views/car_repair_checklist_views.xml',
        'views/car_repair_order_views.xml',
        'views/car_diagnosis_views.xml',
        'wizard/car_diagnosis_assign_technician_wizard_views.xml',
        'views/car_work_order_views.xml',
        'views/sale_order_views.xml',
        'views/menu_views.xml',
        'report/car_repair_report_templates.xml',
        'report/car_repair_report_views.xml',
    ],
    'demo': [
        'demo/car_repair_demo.xml',
    ],
}
