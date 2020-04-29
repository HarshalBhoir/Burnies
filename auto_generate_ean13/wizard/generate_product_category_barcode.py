from odoo import api, fields, models


class GenerateProductCategoryBarcode(models.TransientModel):
    _name = 'generate.product.category.barcode'
    _description = "Generate Product Category Bulk Barcode"

    override_barcode = fields.Boolean('Override Existing Barcode')
    apply_subcategory = fields.Boolean('Apply For Sub Category')

    def generate_barcode(self):
        if self._context.get('active_model') == 'product.category' and self._context.get('active_ids'):
            ctx = dict(self._context)
            for obj in self:
                if obj.apply_subcategory:
                    category_ids = self.env['product.category'].search([('id', 'child_of', self._context.get('active_ids'))])
                else:
                    category_ids = self.env['product.category'].search([('id', 'in', self._context.get('active_ids'))])
                category_ids = [categ.id for categ in category_ids]
                prod_ids = self.env['product.product'].search([('categ_id', 'in', category_ids)])
                if obj.override_barcode:
                    ctx.update({'override_barcode': True})
                    prod_ids.with_context(ctx).generate_barcode()
        return True
