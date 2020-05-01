# -*- coding: utf-8 -*-
#################################################################################
# Author      : Niova IT IVS (<https://niova.dk/>)
# Copyright(c): 2018-Present Niova IT IVS
# License URL : https://invoice-scan.com/license/
# All Rights Reserved.
#################################################################################
from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.company'
    
    default_debitor = fields.Boolean(string='Default Invoice Scan Debitor', copy=False, readonly=True, default=False)