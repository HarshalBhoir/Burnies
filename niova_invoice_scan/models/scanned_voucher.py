# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova IT IVS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova IT IVS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
import sys
from odoo import models, api, fields
import logging
import base64
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

VOUCHER_RECORD_COUNT = 20
MONETARIES = ('total_vat_amount_scanned',
              'total_amount_incl_vat',
              'total_amount_excl_vat',
              'amount',
              'unit_price',
              'ex_vat_amount',
              'incl_vat_amount',
              'discount_amount')

class ScannedVoucher(models.Model):
    _name = 'invoicescan.voucher'
    _description = 'Invoice Scan Voucher'
    _order = 'create_date desc'
    
    invoice_scan_provider = None
    
    state = fields.Selection([('received', 'Received'),
                              ('account_suggest_processing', 'Account Suggest Processing'),
                              ('processing_failed', 'Processing Failed'),
                              ('processed_successfully', 'Processed Successfully'),
                              ('integration_processing', 'Integration Processing'),
                              ('integration_processing_failed', 'Integration Processing Failed '),
                              ('integration_processing_failed_internal_error', 'Integration Processing Failed Internal'),
                              ('integration_processed_successfully ', 'Integration Processed Successfully'), 
                              ('hdr_processing', 'HDR Processing'), 
                              ('processing', 'Processing'), 
                              ('successful', 'Success'), 
                              ('failed', 'Failed'),
                              ('queued', 'Queued'),
                              ('unknown', 'Unknown')], string='Status', readonly=True, default='unknown')
    uploaded_by_email = fields.Char(string="Uploaded by Email", default='')
    country = fields.Char(string="Sender Country", default='')
    company_name = fields.Char(string="Scanned Partner Name", default='', readonly=True)
    voucher_type = fields.Selection([('receipt', 'Receipt'), 
                                     ('invoice', 'Invoice'), 
                                     ('creditnote', 'Credit Note'),
                                     ('reminder', 'Reminder'),
                                     ('account_statement', 'Account Statement'),
                                     ('accountstatement', 'Account Statement'),
                                     ('unknown', 'Unknown')], string="Voucher Type", default='invoice')
    joint_payment_id = fields.Char(string="Joint Payment Id", default='', readonly=True)
    company_vat_reg_no = fields.Char(string="Vat", default='')
    danish_industry_code = fields.Char(string="Danish Industry Code", default='')
    payment_id = fields.Char(string="Payment Id", default='')
    total_vat_amount_scanned = fields.Monetary(string="Tax Amount", default=0, currency_field='currency_id')
    currency = fields.Char(string="Currency", default='')
    voucher_number = fields.Char(string='Voucher Number', default='', readonly=True)
    total_amount_incl_vat = fields.Monetary(string="Gross Amount", default=0, currency_field='currency_id')
    payment_date = fields.Date(string='Scanned Due Date', default='')
    payment_code_id = fields.Char(string="Payment Code", default='')
    invoice_date = fields.Date(string='Invoice Date', default='')
    total_amount_excl_vat = fields.Monetary(string="Net Amount", default=0, currency_field='currency_id')
    creditor_number = fields.Char(string="Creditor Number", default='')
    order_number = fields.Char(string="Vendor Invoice Reference", default='')
    gln_number = fields.Char(string="GLN number", default='')
    payment_reg_number = fields.Char(string="Payment Registration Number", default='')
    payment_account_number = fields.Char(string="Account Number", default='')
    payment_iban = fields.Char(string="Payment Iban Number", default='')
    payment_swift_bic = fields.Char(string="Payment Swift or Bic Number", default='')
    reference = fields.Char(string='Sales Person who send the invoice', default='', help="The partner reference of this invoice.")
    vat_rate = fields.Char(string="Vat Rate", default='')
    penny_difference = fields.Float(string="Payment Rounding ", default=0.0)
    requestor = fields.Char(string="Purchaser who requested the invoice", default='') 
    catalog_debitor_id = fields.Char(string="Debitor", default='')
    note = fields.Char(string="Note", default='')
    payment_method = fields.Char(string="Payment Method", default='')
    
    default_currency = fields.Boolean(string='Default Currency is Used', compute='_compute_currency', default=False, readonly=True, store=True)
    seen = fields.Boolean(string='Voucher Reported', default=False)
    has_invoice = fields.Boolean(string='Invoice Generated', compute='_compute_invoice_generated')
    company_id = fields.Many2one('res.company', string='Debitor', compute='_compute_company', store=True)
    invoice_id = fields.Many2one('account.invoice', string='Invoice Id', readonly=True, ondelete='cascade')
    voucher_id = fields.Integer(string='Scanning Provider ID', help="Reference id to provider of scanning service", default=0, required=True, readonly=True)
    voucher_line_ids = fields.One2many('invoicescan.voucher.line', 'voucher_id', string="Voucher Line Ids", readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency Id', compute='_compute_currency', readonly=True, store=True)
    
    @api.depends('invoice_id')
    def _compute_invoice_generated(self):
        for voucher in self:
            voucher.has_invoice = True if voucher.invoice_id else False
    
    @api.depends('catalog_debitor_id')
    def _compute_company(self):
        for record in self:
            if record.catalog_debitor_id:
                company_id = int((self.env['res.company'].search([('id', '=', int(record.catalog_debitor_id))], limit=1)).id)
                if company_id:
                    record.company_id = company_id
    
    @api.depends('currency')
    def _compute_currency(self):
        for voucher in self:
            currency = self.env['res.currency'].search([('name', '=', voucher.currency)])
            if currency:
                voucher.currency_id = currency.id
                voucher.default_currency = False
            else:
                voucher.currency_id = self.env['account.invoice'].with_context(type='in_invoice')._default_currency().id
                voucher.default_currency = True
    
    @api.multi
    def receive_scanned_vouchers(self, offset=0):
        content = self._get_scan_provider().get_conditional_vouchers(False, False, offset, VOUCHER_RECORD_COUNT)
        
        if content:
            vouchers = content['data']
            vouchers_total_count = content['meta']['count']
            
            # Create vouchers
            for raw_voucher in vouchers:
                self.create_voucher(raw_voucher)

            # Repeat if there are more vouchers
            new_offset = offset + VOUCHER_RECORD_COUNT
            if vouchers_total_count > new_offset: 
                self.receive_scanned_vouchers(new_offset)
    
    @api.multi
    def report_as_done(self):
        # Report to voucher provider that we have computed vouchers to invoices
        vouchers = self.search([('seen', '=', False), ('state', '=', 'successful'), ('invoice_id', '!=', False)])
        if not vouchers:
            return
        voucher_ids = vouchers.mapped('voucher_id')
        status, _, _ = self._get_scan_provider().set_vouchers_as_seen(voucher_ids)
        if not status:
            vouchers.write({'seen': False})
            _logger.exception('Invoice scan: Failed to report {count} vouchers to voucher provider: {voucher_ids}'.format(count=len(voucher_ids), voucher_ids=", ".join(str(i) for i in voucher_ids)))
        else:
            vouchers.write({'seen': True})
            _logger.info('Invoice scan: Successfully reported {count} vouchers to voucher provider: {voucher_ids}'.format(count=len(voucher_ids), voucher_ids=", ".join(str(i) for i in voucher_ids)))
    
    @api.multi
    def get_ready_vouchers(self):
        return self.search([('state', '=', 'successful'), ('invoice_id', '=', False)])
        
    @api.multi
    def create_voucher(self, raw_voucher):
        try:
            vals = self._convert_voucher_values(raw_voucher.get('header_fields', ''))
            vals['voucher_id'] = raw_voucher.get('id')
            vals['uploaded_by_email'] = raw_voucher.get('uploaded_by_email', '')
            vals['state'] = raw_voucher.get('status', 'unknown')
            vals['payment_method'] = raw_voucher.get('user_payment_method', '')
            vals['note'] = raw_voucher.get('note', '')
    
            voucher = self.search([('voucher_id', '=', vals.get('voucher_id'))], limit=1)
            if voucher:
                # Update voucher
                voucher.write(vals)
                self._update_line_items(voucher.id, raw_voucher.get('line_items', []))
            else:
                # Create voucher
                voucher = self.create(vals)
                self._create_line_items(voucher.id, raw_voucher.get('line_items', []))
                voucher._attach_pdf()
            self.env.cr.commit()
        except:
            self.env.cr.rollback()
            error_message  = 'Something went wrong when generating voucher.: {error}'.format(error=sys.exc_info()[0]) 
            _logger.exception(error_message)
    
    @api.multi
    def _attach_pdf(self):
        pdf = self._get_scan_provider().get_voucher_pdf(self.voucher_id)
        if pdf:
            pdf_name = 'invoicescan' + '-' + str(self.voucher_id) + '.pdf'
            
            attachment = {
                'name': pdf_name,
                'datas': base64.encodestring(pdf),
                'datas_fname': pdf_name,
                'res_model': 'invoicescan.voucher',
                'res_id': self.id,
                'type': 'binary',
                'mimetype': 'application/pdf'
            }
            
            try:
                self.env['ir.attachment'].create(attachment)
            except AccessError:
                error_message = 'Cannot save voucher-PDF {error_content} as attachment'.format(error_content=attachment['name'])
                raise error_message
            except:
                error_message = 'Unexpected error occurred when trying to attach voucher-PDF: {error_content}'.format(error_content=sys.exc_info()[0])
                raise error_message
            else:
                _logger.info('The PDF document %s is now saved in the database', attachment['name'])
        else:
            error_message = 'Was not able to get the PDF file from invoice scan: voucher id {error_content}'.format(error_content=self.voucher_id)
            raise error_message
        
    @api.multi
    def _update_line_items(self, voucher_id, line_items):
        # Clear lines and create new once
        voucher_lines = self.env['invoicescan.voucher.line'].search([('voucher_id', '=', voucher_id)])
        if voucher_lines:
            voucher_lines.unlink()
        self._create_line_items(voucher_id, line_items)
    
    @api.multi
    def _create_line_items(self, voucher_id, line_items):
        for item in line_items:
            vals = self._convert_voucher_values(item.get('fields', ''))
            vals['line_id'] = item.get('feature_id')
            vals['voucher_id'] = voucher_id
            self.env['invoicescan.voucher.line'].create(vals)
    
    def _convert_voucher_values(self, data):    
        values = {}
        for field in data:
            code = field.get('code', False)
            value = field.get('value', '')
            if code and value:
                # Convert currency values to positive
                if code in MONETARIES:
                    value = abs(float(value))
                
                # Avoid provider sending unsupported types
                if code == 'voucher_type' and value not in dict(self._fields['voucher_type'].selection):
                    continue
                values[code] = value
        
        return values
    
    def _get_scan_provider(self):
        if not self.invoice_scan_provider:
            self.invoice_scan_provider = self.env['invoicescan.bilagscan']
        return self.invoice_scan_provider
    
    @api.multi
    def action_refresh_voucher(self):
        if self.state != 'successful':
            voucher = self._get_scan_provider().get_voucher(self.voucher_id)
            if voucher:
                self.create_voucher(voucher)
    
class VoucherLines(models.Model):
    _name = 'invoicescan.voucher.line'
    _description = 'Invoice Scan Line'
    
    quantity = fields.Float(string="Quantities", default=0.0)
    unit_price = fields.Float(string="Price pr. Unit", default=0)
    amount = fields.Monetary(string="Amount Scanned", default=0, currency_field='currency_id')
    description = fields.Char(string="Product Description", default='')
    ex_vat_amount = fields.Monetary(string="Net Amount", default=0, currency_field='currency_id')
    incl_vat_amount = fields.Monetary(string="Gross Amount", default=0, currency_field='currency_id')
    account_id = fields.Integer(help="Account Id")
    vat_percentage = fields.Float(string="The Scanned Vat Percent", default=0.0)
    discount_percentage = fields.Float(string="Discount Percentage")
    discount_amount = fields.Float(string="Discount Amount")
    
    line_id = fields.Integer(string='Line ID')
    voucher_id = fields.Many2one('invoicescan.voucher', string="Voucher Ids", required=True, readonly=True, ondelete='cascade')
    currency_id = fields.Many2one('res.currency', related='voucher_id.currency_id', string="Voucher Currency", readonly=True)
        