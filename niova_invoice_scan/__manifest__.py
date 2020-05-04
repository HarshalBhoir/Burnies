# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova IT IVS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova IT IVS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
{
    'name': "Invoice Scan (100% correct scan of vendor bills)",
    'version': '1.2.2',
    'author': "Niova IT",
    'category': 'Accounting',
    'website': 'niova.dk',
    'summery': 'Invoice Scan automatically scans all relevant data from invoices, vendor bills and receipts with 100% accuracy, so digitalization of your Vendor Bill workflow in Odoo becomes complete.',
    'demo': [],
    'depends': ['base_setup', 'account', 'attachment_indexation'],
    'description': """Invoice Scan automatically scans all relevant data from invoices, vendor bills and receipts with 100% accuracy, so digitalization of your Vendor Bill workflow in Odoo becomes complete.""",
    'data': [
        'security/invoice_scan_security.xml',
        'security/ir.model.access.csv',
        'data/invoicescan_data.xml',
        'data/ir_crone_data.xml',
        'data/mail_data.xml',
        'data/mail_template_data.xml',
        'wizard/account_invoice_change_company_view.xml',
        'wizard/account_invoice_change_type_view.xml',
        'wizard/account_invoice_control_view.xml',
        'wizard/invoice_scan_activation_view.xml',
        'wizard/invoice_scan_debitor_view.xml',
        'wizard/invoice_scan_download_view.xml',
        'wizard/invoice_scan_support_view.xml',
        'wizard/invoice_scan_upload_view.xml',
        'views/account_invoice_views.xml',
        'views/assets.xml',
        'views/invoice_scan_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/invoice_scan_menuitem.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'qweb': [
        "static/src/xml/account_invoice.xml"
    ],
    'installable': True,
    'application': True,
    "license":"OPL-1"
}