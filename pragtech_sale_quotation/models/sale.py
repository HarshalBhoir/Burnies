from odoo import api, fields, models ,_

class SaleOrder(models.Model):
    _inherit ="sale.order"
    
    x_amount_total_excl_vat = fields.Monetary(string='Amount Total Excluding Vat')
    x_amount_total_incl_vat = fields.Monetary(string='Amount Total Including Vat')
    x_amount_total_vat = fields.Monetary(string='Amount Total Vat')

class SaleOrderLine(models.Model):
    _inherit ="sale.order.line"
    
    x_product_image = fields.Binary(related='product_id.image_small')
    x_discount_in_amount = fields.Monetary(string="Discount(Amt.)")
    
    @api.multi
    def _prepare_invoice_line(self, qty):
        '''This method override for pass discount_in_amount field from sale to invoice''' 
        res=super(SaleOrderLine, self)._prepare_invoice_line(qty)  
        res.update({'x_discount_in_amount':self.x_discount_in_amount})
        return res
    
    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id','discount')
    def _onchange_discount(self):
        '''This method override for calculate new discount amount field'''
        self.x_discount_in_amount=(self.price_unit*self.product_uom_qty*self.discount)/100
        return super(SaleOrderLine, self)._onchange_discount()  
    
    @api.onchange('x_discount_in_amount')
    def _onchange_discount_in_amount(self):
        '''This method use to update discount from new discount amount field'''
        if self.price_unit and self.product_uom_qty and self.x_discount_in_amount!=0:
            self.discount=(100*self.x_discount_in_amount)/(self.price_unit*self.product_uom_qty)
        else:
            self.discount=0.0
    
     
    
    