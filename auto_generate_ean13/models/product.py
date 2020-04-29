import base64
import functools
import os
from datetime import datetime
from random import randrange

import barcode
from barcode.writer import ImageWriter

from odoo import fields, models, api


def calculate_checksum(ean):
    sum_ = lambda x, y: int(x) + int(y)
    evensum = functools.reduce(sum_, ean[::2])
    oddsum = functools.reduce(sum_, ean[1::2])
    return (10 - ((evensum + oddsum * 3) % 10)) % 10


def generate_ean13(random=True, prefix=None):
    if prefix:
        if random:
            numbers = [randrange(10) for x in range(8)]
        else:
            numbers = [int(a) for a in datetime.today().strftime('%d%H%M%S')]
        numbers = prefix + numbers
    else:
        if random:
            numbers = [randrange(10) for x in range(12)]
        else:
            numbers = [int(a) for a in datetime.today().strftime('%y%m%d%H%M%S')]
    numbers.append(calculate_checksum(numbers))
    return ''.join(map(str, numbers))


def get_ean13_and_image(company, random=True, prefix=None, ean13=None):
    option = {
        'module_width': company.module_width or 0.2,
        'module_height': company.module_height or 15.0,
        'quiet_zone': company.quiet_zone or 0.0,
        'font_size': company.font_size or 10,
        'text_distance': company.text_distance or 5.0,
        'background': company.background or '#000000',
        'foreground': company.foreground or '#FFFFFF',
        'write_text': company.write_text or False,
    }
    if not ean13:
        ean13 = generate_ean13(random=random, prefix=prefix)
    print("ean13  :  ", ean13)
    ean = barcode.get('ean13', ean13, writer=ImageWriter())
    filename = ean.save('/tmp/' + ean13, options=option)
    print("filename  : ", filename)
    # r = open(filename, 'rb').read()  # .encode('base64')
    r = base64.b64encode(open(filename, 'rb').read())
    os.remove(filename)
    return r, ean13


class ProductProduct(models.Model):
    _inherit = 'product.product'

    ean13_image = fields.Binary("EAN13 image")

    def generate_ean13_barcode(self, barcode=None):
        # Check Context and company
        company = self.env['res.company'].browse(self._context.get('company_id'))
        if company.use_prefix and company.prefix:
            prefix = [int(a) for a in company.prefix]
            if company.generate_method == 'current_date':
                ean13_image, ean13 = get_ean13_and_image(company, random=False, prefix=prefix, ean13=barcode)
            else:
                ean13_image, ean13 = get_ean13_and_image(company, random=True, prefix=prefix, ean13=barcode)
        else:
            if company.generate_method == 'current_date':
                ean13_image, ean13 = get_ean13_and_image(company, random=False, prefix=None, ean13=barcode)
            else:
                ean13_image, ean13 = get_ean13_and_image(company, random=True, prefix=None, ean13=barcode)

        if not barcode:  # If barcode is passed then return computed ean13 and image
            if not self.search([('barcode', '=', ean13)]):
                return ean13_image, ean13
            else:  # Return False if same barcode is already exist
                return False, False
        else:  # If barcode is passed then return same ean13 and computed image
            return ean13_image, ean13

    @api.model
    def create(self, vals):
        ctx = dict(self._context)
        if vals.get('company_id'):
            company = self.env['res.company'].browse(vals.get('company_id'))
            ctx.update({'company_id': vals.get('company_id')})
        elif self._context.get('company_id'):
            company = self.env['res.company'].browse(self._context.get('company_id'))
            ctx.update({'company_id': self._context.get('company_id')})
        else:
            company = self.env['res.company']._company_default_get('product.template')
            ctx.update({'company_id': company.id})
        if company.on_product_creation:
            ean13_image, ean13 = self.with_context(ctx).generate_ean13_barcode(vals.get('barcode'))
            if ean13:
                vals.update({'barcode': ean13, 'ean13_image': ean13_image})
        return super(ProductProduct, self).create(vals)

    def generate_barcode(self):
        ctx = dict(self._context)
        for product in self:
            ean13 = None
            if product.company_id:
                ctx.update({'company_id': product.company_id.id})
            else:
                company = self.env['res.company']._company_default_get('product.template')
                ctx.update({'company_id': company.id})
            if self._context.get('override_barcode'):
                ean13_image, ean13 = product.with_context(ctx).generate_ean13_barcode()
                while self.search([('barcode', '=', ean13)]):
                    ean13_image, ean13 = product.with_context(ctx).generate_ean13_barcode()
            elif product.barcode:
                if not product.ean13_image:
                    ean13_image, ean13 = product.with_context(ctx).generate_ean13_barcode(product.barcode)
            else:  # Not Barcode:
                ean13_image, ean13 = product.with_context(ctx).generate_ean13_barcode(product.barcode)
                while self.search([('barcode', '=', ean13)]):
                    ean13_image, ean13 = product.with_context(ctx).generate_ean13_barcode(product.barcode)
            if ean13:
                product.write({'barcode': ean13, 'ean13_image': ean13_image})
        return True
