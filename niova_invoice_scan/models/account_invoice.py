# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova IT IVS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova IT IVS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
import sys
from odoo import models, api, fields, _
import logging
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)

ROUNDING_DECIMAL = 3
# mapping scanned voucher to invoice type
VOUCHER2INVOICE = {
    'receipt': 'in_invoice',
    'invoice': 'in_invoice',
    'creditnote': 'in_refund',
    'unknown': 'in_invoice',
    'reminder': 'in_invoice',
    'account_statement': 'in_invoice',
    'accountstatement': 'in_invoice',
}

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    voucher_id = fields.Many2one('invoicescan.voucher', string='Voucher Id', ondelete='set null', readonly=True)
    voucher_active = fields.Boolean(string='Scanned Lines', default=False, copy=False, readonly=True, states={'draft': [('readonly', False)]}, help="Mark this field to use scanned lines from invoice scan.")
    difference = fields.Monetary(string="Control Value", default=0, currency_field='currency_id', compute='_onchange_amount_differnce', readonly=True)    
    partner_id = fields.Many2one('res.partner', 
                                 string='Partner', 
                                 change_default=True,
                                 required=False,
                                 readonly=True, 
                                 states={'draft': [('readonly', False), ('required', True)],
                                         'open': [('required', True)],
                                         'paid': [('required', True)],
                                         'cancel': [('required', True)]},
                                 track_visibility='always')
    payment_date = fields.Date(related='voucher_id.payment_date', readonly=True)
    requestor = fields.Char(related='voucher_id.requestor', readonly=True)
    purchase_reference = fields.Char(related='voucher_id.reference', readonly=True)
    total_amount_incl_vat = fields.Monetary(related='voucher_id.total_amount_incl_vat', readonly=True)
    total_vat_amount_scanned = fields.Monetary(related='voucher_id.total_vat_amount_scanned', readonly=True)
    total_amount_excl_vat = fields.Monetary(related='voucher_id.total_amount_excl_vat', readonly=True)
    voucher_company_name = fields.Char(related='voucher_id.company_name', readonly=True)
    voucher_line_ids = fields.One2many(related='voucher_id.voucher_line_ids', readonly=True)
    voucher_line_count = fields.Integer(string='Scanned Lines', compute='_compute_voucher_line_count', readonly=True)
    duplicated_invoice_ids = fields.Many2many('account.invoice', 'invoice_related_invoice_rel', 'invoice_id','invoice_related_id', string='Duplicated Invoice IDs', readonly=True)
    default_currency_used = fields.Boolean(string='Default Currency is Used', default=False, readonly=True)
    scanning_provider_id = fields.Integer(related='voucher_id.voucher_id', readonly=True)

    @api.multi
    def name_get(self):
        """ Many2many display name"""
        vals = []
        for record in self:
            if record.number:
                val = record.number
            else: 
                val = 'BILL/ID/{id}'.format(id = record.id)
            vals.append((record.id, val))
        return vals
        
    @api.onchange('voucher_line_ids')
    def _compute_voucher_line_count(self):
        for invoice in self:
            invoice.voucher_line_count = len(invoice.voucher_line_ids)
    
    @api.onchange('total_amount_incl_vat', 'amount_total')
    def _onchange_amount_differnce(self):
        for invoice in self:
            differnce = invoice.amount_total - invoice.voucher_id.total_amount_incl_vat
            invoice.difference = differnce
    
    @api.multi
    def _generate_invoices(self):
        InvoiceScan = self.env['invoicescan.voucher']
        
        # Get vouchers
        vouchers = InvoiceScan.get_ready_vouchers()
        if not vouchers:
            return 
        
        completed_vouchers = []
        for voucher in vouchers:
            # Create invoice
            invoice = self._create_invoice(voucher)
            
            # Continue if the invoice creation failed
            if not invoice:
                continue
            
            # Save voucher ID to report to voucher provider
            completed_vouchers.append(voucher.voucher_id)
            
            # Post process invoice
            invoice._post_process_generated_invoice()
            
        # Report to voucher provider
        InvoiceScan.report_as_done()
        _logger.info('Invoice scan: Successfully created {count} invoices: {voucher_ids}'.format(count=len(completed_vouchers), voucher_ids=", ".join(str(i) for i in completed_vouchers)))
    
    @api.multi
    def _post_process_generated_invoice(self):
        for invoice in self:
            #-------------------#
            # ---- Features ----#
            #-------------------#
            
            #Attach auto generated invoice line or voucher lines
            invoice._auto_attach_invoice_lines()
            
            # Auto validate invoice
            invoice._auto_validate()
    
    @api.multi
    def _create_invoice(self, voucher):
        try:
            inv_type = VOUCHER2INVOICE.get(voucher.voucher_type, 'in_invoice')
            vals = {
                'type': inv_type,
                'state': 'draft',
                'voucher_id': voucher.id,
                'reference': voucher.voucher_number,
                'date_invoice': voucher.invoice_date,
                'default_currency_used': voucher.default_currency
                }
            vals = self._check_duplicated_invoices(voucher, vals)
            vals = self._add_currency(vals, voucher)
            vals = self._add_fik(vals, voucher)
            vals = self._add_company(vals, voucher)
            # Add partner must be after a company has been selected
            vals = self._add_partner_values(vals, voucher)
            vals = self._add_journal(vals)
            
            # Create invoice
            invoice = self.with_context(default_type=inv_type, type=inv_type, company_id=vals.get('company_id'), force_company=vals.get('company_id')).create(vals)
            invoice._onchange_payment_term_date_invoice()
            voucher.invoice_id = invoice.id
      
            # Attach PDF to invoice
            invoice._attach_pdf(voucher)
            
            # Add notes
            invoice._add_note(voucher)
            self.env.cr.commit()
            return invoice
        except:
            self.env.cr.rollback()
            _logger.exception('Invoice (voucher id: {voucher_id}) was not created due to an unexpected error: {error_content}'.format(error_content=sys.exc_info()[0], voucher_id=voucher.id))
        return False
    
    @api.multi
    def _add_note(self, voucher):
        note = ''
        if voucher.payment_method:
            note = '<strong>Recommended payment method</strong>: {payment_method}<br/>'.format(payment_method=voucher.payment_method)
        if voucher.note:
            note = note + '<strong>Invoice note</strong>: {note}'.format(note=voucher.note)
        if note:
            self.message_post(body=_(note))

    @api.multi
    def _attach_pdf(self, voucher):
        attachments = self.env['ir.attachment'].search([('res_model', '=', voucher._name),
                                                        ('res_id', '=', voucher.id)])
        if attachments:
            # move attachments
            attachments.write({'res_model': self._name, 'res_id': self.id})
        
    def _check_duplicated_invoices(self, voucher, vals):
        domain = ['|', ('voucher_id', '=', voucher.voucher_id),
                       ('reference', '=', voucher.voucher_number),
                       ('voucher_id.joint_payment_id', '=', voucher.joint_payment_id),
                       ('voucher_company_name', '=', voucher.company_name)]
        
        # Check if there already is an voucher created
        duplicated_invoices = self.search(domain)
        if duplicated_invoices:
            invoice_ids = []
            for duplicated_invoice in duplicated_invoices:
                invoice_ids.append(duplicated_invoice.id)
            
            vals['duplicated_invoice_ids'] = [(6, 0, invoice_ids)]
        return vals
    
    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
        company_id = self.company_id.id
        partner = self.partner_id if not company_id else self.partner_id.with_context(force_company=company_id)
        if partner:
            self.fiscal_position_id = self.env['account.fiscal.position'].with_context(force_company=company_id).get_fiscal_position(partner.id)
        return res

    @api.onchange('payment_term_id', 'date_invoice')
    def _onchange_payment_term_date_invoice(self):
        date_invoice = self.date_invoice
        if not date_invoice:
            date_invoice = fields.Date.context_today(self)
        if self.payment_term_id:
            pterm = self.payment_term_id
            pterm_list = pterm.with_context(currency_id=self.company_id.currency_id.id).compute(value=1, date_ref=date_invoice)[0]
            self.date_due = max(line[0] for line in pterm_list)
        elif self.voucher_id:
            if self.voucher_id.payment_date:
                self.date_due = self.voucher_id.payment_date

        if self.date_due and (date_invoice > self.date_due):
            self.date_due = date_invoice

    @api.onchange('currency_id')
    def _onchange_currency(self):
        self.default_currency_used = False

    @api.multi
    def _add_currency(self, vals, voucher):
        if voucher.currency_id.id:
            vals['currency_id'] = voucher.currency_id.id
        return vals
    
    @api.multi
    def _add_fik(self, vals, voucher):
        if voucher.payment_code_id and voucher.payment_id and voucher.joint_payment_id:
            if self._fields.get('fik_number', False):
                vals['fik_number'] = '+%s<%s+%s<' % (voucher.payment_code_id, voucher.payment_id, voucher.joint_payment_id)
            
            if self._fields.get('fik_payment_code', False) and voucher.payment_code_id in self._fields.get('fik_payment_code').selection:
                vals['fik_payment_code'] = voucher.payment_code_id
            if self._fields.get('fik_payment_id', False):
                vals['fik_payment_id'] = voucher.payment_id
            if self._fields.get('fik_creditor_id', False):
                vals['fik_creditor_id'] = voucher.joint_payment_id
        return vals
    
    @api.multi
    def _add_account(self, vals, default_account_id=False):
        if default_account_id:
            account_id = default_account_id
        else:
            account_id = self.env['ir.property'].with_context(force_company=vals['company_id']).get('property_account_payable_id', 'res.partner')
            
        vals['account_id'] = int(account_id)
        return vals
    
    @api.multi
    def _add_company(self, vals, voucher):
        if voucher.company_id:
            company_id = voucher.company_id.id
        else:
            company_id = 1
                    
        vals['company_id'] = company_id
        return vals

    @api.multi
    def _add_journal(self, vals):
        if vals['company_id']:
            journal_id = self.with_context(company_id=vals['company_id'], type=vals['type'])._default_journal().id
        else:
            journal_id = 1

        vals['journal_id'] = journal_id
        return vals

    @api.multi
    def _add_partner_values(self, vals, voucher):
        domain = []
        partner = False
        if voucher.company_vat_reg_no:
            domain.append(('vat', 'ilike', voucher.company_vat_reg_no))
        if voucher.company_name:
            domain.append(('name', 'ilike', voucher.company_name))
            domain.append(('alias', 'ilike', voucher.company_name))
        
        if len(domain) > 2:
            domain.insert(0, '|')
            domain.insert(2, '|')
        elif len(domain) > 1: 
            domain.insert(0, '|')

        if domain:
            partner = self.env['res.partner'].with_context(force_company=vals['company_id']).search(domain, limit=1)

        # Default values
        vals = self._add_account(vals)
        if partner:
            vals['partner_id'] = partner.id
            
            if not partner.property_account_payable_id:
                raise Exception('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
            vals = self._add_account(vals, partner.property_account_payable_id.id)
 
            if partner.property_supplier_payment_term_id:
                vals['payment_term_id'] = int(partner.property_supplier_payment_term_id.id)

        return vals
    
    @api.multi
    def action_voucher_lines_wizard(self):
        self.ensure_one()
        compose_form = self.env.ref('niova_invoice_scan.view_voucher_lines_wizard_tree', False)
        return {
            'name': _('Scanned Voucher Lines'),
            'res_model': 'invoicescan.voucher.line',
            'domain': [('id', 'in', [x.id for x in self.voucher_id.voucher_line_ids])],
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(compose_form.id, 'tree')],
            'view_id': compose_form.id,
            'target': 'new',
            'res_id': self.id
        }
    
    @api.multi
    def action_voucher_wizard(self):
        self.ensure_one()
        compose_form = self.env.ref('niova_invoice_scan.view_voucher_wizard_form', False)
        return {
            'name': _('Scanned Voucher'),
            'res_model': 'invoicescan.voucher',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'res_id': self.voucher_id.id
        }
         
    @api.onchange('voucher_active')
    def toggle_voucher_active(self):
        for invoice in self:
            invoice.voucher_active = not invoice.voucher_active
            if not invoice._attach_voucher_lines():
                invoice.voucher_active = not invoice.voucher_active
    
    @api.multi
    def _attach_single_invoice_line(self):
        line_values = {'invoice_id': self.id,
                       'name': self.partner_id.property_default_invoice_line_description,
                       'account_id': self.partner_id.property_default_expense_account_id,
                       'price_unit': self.total_amount_excl_vat if self.total_amount_excl_vat else self.total_amount_incl_vat,
                       'invoice_line_tax_ids': [(6, 0, self.partner_id.property_default_invoice_line_tax_id._ids)],
                       'quantity': 1}
        new_line = self.env['account.invoice.line'].new(line_values)
        new_line._set_additional_fields(self)    
        self.invoice_line_ids = new_line
        # Apply the taxes
        self._onchange_invoice_line_ids()
    
    @api.multi         
    def _attach_voucher_lines(self):
        # If unselect is made, then unlink all voucher lines
        if not self.voucher_active:
            for invoice_line in self.invoice_line_ids.filtered(lambda r: r.voucher_line_id != False):
                invoice_line.unlink()
            # Remove the taxes
            self._onchange_invoice_line_ids()       
        # Else add voucher lines from the voucher to the invoice
        else:   
            new_lines = self.env['account.invoice.line']
            for line in self.voucher_id.voucher_line_ids - self.invoice_line_ids.mapped('voucher_line_id'):
                data = self._prepare_invoice_line_from_voucher_line(line)
                new_line = new_lines.new(data)
                new_line._set_additional_fields(self)
                new_line._onchange_account_id()
                new_lines += new_line
    
            self.invoice_line_ids += new_lines
            # Apply the taxes
            self._onchange_invoice_line_ids()
        return True

    @api.multi
    def _prepare_invoice_line_from_voucher_line(self, line):
        account_id = self.env['account.invoice.line'].with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice', 'partner_id': self.partner_id.id })._default_account()
        quantity = self._compute_quantity(line.quantity)
        unit_price, discount_percentage = self._compute_unit_price(line.amount, quantity, line.discount_percentage, line.discount_amount)
        
        data = {
            'invoice_id': self.id,
            'voucher_line_id': line.id,
            'name': line.description,
            'account_id': account_id,
            'price_unit': unit_price,
            'quantity': quantity,
            'discount': discount_percentage
        }
        return data

    @api.multi
    def _compute_quantity(self, quantity):
        if quantity:
            return quantity
        return 1
    
    @api.multi
    def _compute_unit_price(self, amount, qty, discount_percentage, discount_amount):
        if not amount:
            return 0.0, 0.0
        
        unit_price = round(amount/qty, ROUNDING_DECIMAL)
        return self._compute_discount(unit_price, discount_amount, discount_percentage)
    
    @api.multi
    def _compute_discount(self, unit_price, discount_amount, discount_percentage):
        if discount_percentage:
            discount_percentage = round(discount_percentage, ROUNDING_DECIMAL)
        elif discount_amount:
            discount_percentage = round(discount_amount/(unit_price + discount_amount)*100, ROUNDING_DECIMAL)
        else:
            return unit_price, 0.0
        
        unit_price = (unit_price/(100-discount_percentage))*100
        discount_amount = round(discount_percentage/100 * unit_price, ROUNDING_DECIMAL)
        return unit_price, discount_percentage
    
    @api.multi
    def _auto_validate(self):
        if self.partner_id.property_auto_validate_invoice and self.difference == 0 and self.total_amount_incl_vat > 0 and self.partner_id:
            try:
                self.action_invoice_open()
                self.env.cr.commit()
            except:
                self.env.cr.rollback()
                _logger.exception('Invoice (invoice id: {invoice_id}) did not auto validate due to an unexpected error: {error_content}'.format(error_content=sys.exc_info()[0], invoice_id=self.id))
    
    @api.multi
    def _auto_attach_invoice_lines(self):
        if self.partner_id:
            try:
                # Attach single invoice line or voucher lines
                if self.partner_id.property_auto_apply_single_invoice_line:
                    self._attach_single_invoice_line()
                elif self.partner_id.property_auto_apply_voucher_lines:
                    self.toggle_voucher_active()
                self.env.cr.commit()
            except:
                self.env.cr.rollback()
                _logger.exception('Invoice (invoice id: {invoice_id}) did not add invoice lines due to an unexpected error: {error_content}'.format(error_content=sys.exc_info()[0], invoice_id=self.id))

                
class AccountInvoiceLine(models.Model):
    """ Override AccountInvoice_line to add the link to the scanned voucher line it is related to"""
    _inherit = 'account.invoice.line'
    
    @api.model
    def _default_account(self):
        if self._context.get('partner_id'):
            partner = self.env['res.partner'].browse(self._context.get('partner_id'))
            if partner.property_default_expense_account_id:
                return partner.property_default_expense_account_id.id
        return super(AccountInvoiceLine, self)._default_account()
    
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Invoicescan Price Unit'))
    account_id = fields.Many2one(default=_default_account)
    voucher_line_id = fields.Many2one('invoicescan.voucher.line', 'Scanned Order Line', ondelete='set null', readonly=True)
    voucher_id = fields.Many2one('invoicescan.voucher',related='voucher_line_id.voucher_id', string='Scanned Voucher', store=False, readonly=True, related_sudo=False,
        help='Associated Scanned Voucher.')
    
    @api.onchange('account_id')
    def _onchange_account_id(self):
        super(AccountInvoiceLine, self)._onchange_account_id()
        if not self.product_id and self.partner_id and self.partner_id.property_default_invoice_line_tax_id:
            self.invoice_line_tax_ids = [(6, 0, self.partner_id.property_default_invoice_line_tax_id._ids)]

    @api.onchange('uom_id')
    def _onchange_uom_id(self):
        old_price_unit = False
        if self.voucher_id:
            old_price_unit = self.price_unit if self.price_unit else False
        res = super(AccountInvoiceLine, self)._onchange_uom_id()
        self.price_unit = old_price_unit if old_price_unit else self.price_unit
        return res
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        old_name = False
        if self.voucher_id:
            old_name = self.name if self.name else False
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        self.name = old_name if old_name else self.name
        return res
