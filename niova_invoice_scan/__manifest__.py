# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova IT IVS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova IT IVS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
{
    'name': "Invoice Scan (100% correct)",
    'version': '1.0.13',
    'author': "Niova IT",
    'category': 'Accounting',
    'website': 'niova.dk',
    'summery': 'Invoice Scan automatically scans all relevant data from invoices, vendor bills and receipts regardless of format with 100% accuracy, so digitalization of your workflow in Odoo becomes complete.',
    'demo': [],
    'depends': ['base_setup', 'account', 'document'],
    'description': """Invoice Scan automatically scans all relevant data from invoices, vendor bills and receipts regardless of format with 100% accuracy, so digitalization of your workflow in Odoo becomes complete.""",
    'data': [
        'wizard/invoice_scan_support_view.xml',
        'security/ir.model.access.csv',
        'data/ir_crone_data.xml',
        'data/invoicescan_data.xml',
        'data/mail_template_data.xml',
        'views/assets.xml',
        'views/account_invoice_views.xml',
        'views/res_config_settings_views.xml',
        'views/invoice_scan_views.xml',
        'views/res_partner_views.xml'
    ],
    'images': [
        'static/description/banner.png',
    ],
    'qweb': [
        "static/src/xml/account_invoice.xml"
    ],
    'installable': True,
    'application': False,
    "license":"OPL-1"
}