# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova IT IVS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova IT IVS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, fields, api

class Partner(models.Model):

    _inherit = 'res.partner'
    
    # Backward compatibility
    default_expense_account_id = fields.Many2one('account.account', string='Default Invoice Line Account', company_dependent=True, help='This account will be used on the vendor bill lines as default')
    payment_journal_id = fields.Many2one('account.journal', string='Payment Method', company_dependent=True, domain="[('type', 'in', ['cash', 'bank'])]")
    
    alias = fields.Char('Alias')
    property_default_expense_account_id = fields.Many2one('account.account', string='Default Line Expense Account', company_dependent=True, help='This account will be used on the vendor bill lines as default')
    
    # Automation
    property_auto_validate_invoice = fields.Boolean(string='Auto Validate Vendor Bill', company_dependent=True, default=False, help='Auto Validate Invoice if the control value is 0')
    property_auto_apply_voucher_lines = fields.Boolean(string='Auto Apply Scanned Lines', company_dependent=True, default=False, help='Auto Apply Scanned Lines')
    property_auto_apply_single_invoice_line = fields.Boolean(string='Auto Generate Invoice Line', company_dependent=True, default=False, help='Auto generate a invoice line with the total amounts from the vendor bill')
    
    # Single invoice line generation
    property_default_invoice_line_description = fields.Char(string='Default Invoice Line Description', company_dependent=True, help='The default description on the invoice line')
    property_default_invoice_line_tax_id = fields.Many2one('account.tax',
                                                             company_dependent=True,
                                                             string='Default Invoice Line Tax',
                                                             domain=[('type_tax_use','!=','none'), '|', ('active', '=', False), ('active', '=', True)], 
                                                             help='Default taxes on invoice line.')
    
    @api.onchange('property_auto_apply_single_invoice_line')
    def _onchange_auto_apply_single_invoice_line(self):
        for partner in self:
            # Auto validation may not be activated along with auto single invoice line generation.
            # This will then auto complete every incoming invoice, because the control values will always be zero.
            # It does not make sense to validate invoices without lines
            if partner.property_auto_apply_single_invoice_line:
                partner.property_auto_apply_voucher_lines = False
                partner.property_auto_validate_invoice = False

    @api.onchange('property_auto_apply_voucher_lines', 'property_auto_validate_invoice')
    def _onchange_auto_apply_voucher_lines(self):
        for partner in self:
            # Auto validation may not be activated along with auto single invoice line generation.
            # This will then auto complete every incoming invoice, because the control values will always be zero.
            # It does not make sense to validate invoices without lines
            if partner.property_auto_apply_voucher_lines:
                partner.property_auto_apply_single_invoice_line = False
                
            if partner.property_auto_validate_invoice:
                partner.property_auto_apply_single_invoice_line = False
                partner.property_auto_apply_voucher_lines = True
    
            
            
