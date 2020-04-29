from odoo import api, fields, models


class GenerateProductBarcode(models.TransientModel):
    _name = 'generate.product.barcode'
    _description = "Generate Product Bulk Barcode"

    override_barcode = fields.Boolean('Override Existing Barcode')

    def generate_barcode(self):
        if self._context.get('active_model') == 'product.product' and self._context.get('active_ids'):
            ctx = dict(self._context)
            for obj in self:
                if obj.override_barcode:
                    ctx.update({'override_barcode': True})
                self.env['product.product'].browse(self._context.get('active_ids')).with_context(ctx).generate_barcode()
        return True
