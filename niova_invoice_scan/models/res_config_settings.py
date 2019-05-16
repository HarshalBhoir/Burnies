# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova IT IVS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova IT IVS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    module_niova_invoice_scan = fields.Boolean(string='Allow the invoice to be synchronize by invoice scan')
    is_client_secret = fields.Char("Activation Key")
    is_mail_forward_address = fields.Char("Forward Email", readonly=True)

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].set_param
        set_param('invoice_scan_client_secret', (self.is_client_secret or '').strip())
        set_param('invoice_scan_mail_forward_address', (self.is_mail_forward_address or '').strip())
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            is_client_secret = get_param('invoice_scan_client_secret', default=False),
            is_mail_forward_address = get_param('invoice_scan_mail_forward_address', default=False)
        )
        return res

    @api.multi
    def reactivate_invoice_scan(self):
        self.env['invoicescan.manager'].reset(self.is_client_secret)
        set_param = self.env['ir.config_parameter'].set_param
        set_param('invoice_scan_client_secret', '')
        set_param('invoice_scan_mail_forward_address', '')
        self.write({'is_client_secret': False, 'is_mail_forward_address': False})
        self._activate_cron(False)
        return self.env.ref('base_setup.action_general_configuration').read()[0]
    
    @api.multi
    def activate_invoice_scan(self):
        set_param = self.env['ir.config_parameter'].set_param
        set_param('invoice_scan_client_secret', (self.is_client_secret or '').strip())
        response = self.env['invoicescan.manager'].activate(self.is_client_secret)
        if not response:
            raise UserError(_("Activation failed. This may due to wrong secret."))
        self._activate_cron()
        return self.env.ref('base_setup.action_general_configuration').read()[0]
    
    @api.multi
    def _activate_cron(self, activate=True):
        scan_service = self.env.ref('niova_invoice_scan.ir_crone_invoice_scan_service')
        if scan_service:
            cron = self.env['ir.cron'].browse(scan_service.id)
            if cron:
                cron.try_write({'active': activate})
    
    @api.multi
    def recieve_activation_key(self):
        return self.env['invoicescan.manager'].redirect_to_invoicescan()
    
    @api.multi
    def action_upload_debitors(self):
        companies = self.env['res.company'].search([])
        debitors = []
        for company in companies:
            partner = company.partner_id
            
            def convert_values(value):
                return str(value) if value else ''
            
            debitor = {
                  "id": convert_values(company.id),
                  "group_id": 1,
                  "name": convert_values(company.name),
                  "alias": convert_values(partner.alias),
                  "address_1": convert_values(partner.street),
                  "address_2": convert_values(partner.street2),
                  "zip_code": convert_values(partner.zip),
                  "city": convert_values(partner.city),
                  "country": convert_values(partner.country_id.name),
                  "email": convert_values(company.email),
                  "keyWords": [
                    {
                      "type": "cvr",
                      "value": convert_values(company.company_registry)
                    }
                  ]
                }
            debitors.append(debitor)

        status, _, _ = self.env['invoicescan.bilagscan'].set_debitors(debitors)
        
        if not status:
            raise UserError(_("The debitors were not successful uploaded to Invoice Scan."))
