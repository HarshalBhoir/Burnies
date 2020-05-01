# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova IT IVS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova IT IVS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, api, fields

TO_EMAIL = 'support@bilagscan.dk'

class InvoiceScanSupport(models.TransientModel):
    _name = 'invoicescan.support'
    _description = 'Invoice Scan Support'
    
    name = fields.Char('Name')
    note = fields.Text('Note', required=True)
    email_to = fields.Char('To Email')
    email_from = fields.Char('From Email')
    scanning_provider_id = fields.Integer('Voucher ID', readonly=True)
    
    def action_send_email(self):
        self.name = self.env.user.name
        self.email_to = TO_EMAIL
        self.email_from = self.env.user.login if self.env.user.login else self.env.user.company_id.email
        template = self.env.ref('niova_invoice_scan.email_template_invoice_scan')
        self.env['mail.template'].browse(template.id).send_mail(self.id)