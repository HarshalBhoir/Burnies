from odoo import api, fields, models ,_

class InvoiceLine(models.Model):
    _inherit ="account.invoice.line"
    
#     product_image = fields.Binary(related='product_id.image_small')
    x_discount_in_amount = fields.Monetary(string="Discount(Amt.)")
    
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        '''This method override for calculate new discount amount field'''
        self.x_discount_in_amount=(self.price_unit*self.quantity*self.discount)/100
        return super(InvoiceLine, self)._compute_price()
    
    @api.onchange('x_discount_in_amount')
    def _onchange_discount_in_amount(self):
        '''This method use to update discount from new discount amount field'''
        if self.price_unit and self.quantity and self.x_discount_in_amount!=0:
            self.discount=(100*self.x_discount_in_amount)/(self.price_unit*self.quantity)
        else:
            self.discount=0.0