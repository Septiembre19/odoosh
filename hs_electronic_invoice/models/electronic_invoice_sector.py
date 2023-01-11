# -*- coding: utf-8 -*-
from odoo import models, fields, api


class electronic_invoice_sector(models.Model):
    _name = 'electronic.invoice.sector'
    code = fields.Char(string='Código', size=3)
    name = fields.Char(string='Nombre', size=255, translate=True)
    country_id = fields.Many2one('res.country', string='País',
                                 compute='_get_country_id', store=True)
    province_id = fields.Many2one(
        'electronic.invoice.province', string='Provincia')
    fe_district_id = fields.Many2one(
        'electronic.invoice.district', string='Distrito')

    @api.depends('name')
    def _get_country_id(self):
        country = self.pool.get('res.country')
        country_id = self.env['res.country'].search(
            [['code', '=', 'PAN']]).id
        self.country_id = country_id
