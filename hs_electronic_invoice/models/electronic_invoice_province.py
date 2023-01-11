# -*- coding: utf-8 -*-
from odoo import models, fields, api


class electronic_invoice_province(models.Model):
    _name = 'electronic.invoice.province'
    code = fields.Char(string='Código', size=3)
    name = fields.Char(string='Nombre', size=255, translate=True)
    country_id = fields.Many2one('res.country', string='País',
                                 compute='_get_country_id', store=True, ondelete='cascade')
    district_ids = fields.One2many(
        'electronic.invoice.district', 'province_id', string='Distritos')

    @api.depends('name')
    def _get_country_id(self):
        country = self.pool.get('res.country')
        country_id = self.env['res.country'].search([['code', '=', 'PA']]).id
        self.country_id = country_id
