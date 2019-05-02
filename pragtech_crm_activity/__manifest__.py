# -*- coding: utf-8 -*-
{
    'name': 'Pragtech CRM Activity',
    'version': '1.0',
    'author': 'Pragmatic Techsoft Pvt. Ltd.',
    'website': 'http://www.pragtech.co.in',
    'category': 'CRM',
    'summary': """This module adds and modify CRM Module functionality""",
    'depends': ['base', 'crm', 'mail'],
    'data': [
        'views/mail_activity_views.xml',
        'views/crm_lead_views.xml',
        'views/template.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True, 
    'auto_install': False,
    'application': True,
}
