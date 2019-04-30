# -*- coding: utf-8 -*-
{
    'name': 'Pragtech Email Compose',
    'version': '1.0',
    'author': 'Pragmatic Techsoft Pvt. Ltd.',
    'website': 'http://www.pragtech.co.in',
    'category': 'Contacts',
    'summary': """This module adds compose and send mail functionality in customer master""",
    'depends': ['base', 'mail'],
    'data': [
        'data/mail_data.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
