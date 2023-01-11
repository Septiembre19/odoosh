# -*- coding: utf-8 -*-

from dataclasses import field
from email.policy import default
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime
import logging


class customers_fields(models.Model):
    #_inherit = "product.product"
    #_name = "res.partner"
    _inherit = "res.partner"
    # asignar campos al modulo de res.partner

    @api.depends('name')
    def _get_country_id(self):
        country = self.pool.get('res.country')
        country_id = self.env['res.country'].search(
            [['name', '=', 'Panama']]).id
        self.country_id = country_id

    is_company_config = fields.Boolean('Has FE', compute='compute_active_fe')

    TipoClienteFE = fields.Selection(
        string='Tipo Cliente',
        selection=[
            ('00', ''),
            ('01', 'Contribuyente'),
            ('02', 'Consumidor final'),
            ('03', 'Gobierno'),
            ('04', 'Extranjero')
        ])
    # default=lambda self: self._get_type_client()

    tipoContribuyente = fields.Selection(
        [('1', 'Natural'),
         ('2', 'Jurídico')], string='Tipo Contribuyente', compute="_compute_tipoIdent")
    numeroRUC = fields.Char(string="Cédula o RUC", size=20)
    digitoVerificadorRUC = fields.Char(string="Dígito Verificador RUC", size=2)
    #razonSocial = fields.Char(string="Razón Social", size=100)
    #direccion = fields.Char(string="Dirección", size=100)
    # ubicacion change
    #neonety_country_id = fields.Many2one('res.country', string='País', default=lambda self: self._get_country_id())
    country_id = fields.Many2one(
        'res.country', string='País',
        default=lambda self: self._get_country_id()
    )
    province_id = fields.Many2one(
        'electronic.invoice.province', string='Provincia')
    fe_district_id = fields.Many2one(
        'electronic.invoice.district', string='Distrito')
    sector_id = fields.Many2one(
        'electronic.invoice.sector', string='Corregimiento')
    # codigo
    CodigoUbicacion = fields.Char(string="Codigo Ubicación", size=8)
    provincia = fields.Char(string="Provincia", related='province_id.code')
    distrito = fields.Char(string="Distrito", related='fe_district_id.code')
    corregimiento = fields.Char(
        string="Corregimiento", related='sector_id.code')
    tipoIdentificacion = fields.Selection(
        [('01', 'Pasaporte'),
         ('02', 'Numero Tributario'),
         ('99', 'Otro')], string='Tipo Identificación')
    nroIdentificacionExtranjero = fields.Char(
        string="Nro. de Pasaporte o Nro. de Identificación Tributaria Extranjera")
    # paisExtranjero = fields.Char(string="País Extranjero", size=50,
    # 							 help="Solo se utiliza si se llena el campo Nro. de Pasaporte o Nro. de Identificación Tributaria Extranjera con el pasaporte (Utilizar nombre completo del país).")
    # telefono1	 ///correoElectronico1
    pais = fields.Char(string="País")
    paisOtro = fields.Char(string="País Otro", size=50)

    @api.depends('TipoClienteFE')
    def _compute_tipoIdent(self):
        if str(self.TipoClienteFE) == '01' or str(self.TipoClienteFE) == '03':
            self.tipoContribuyente = '2'
            self.company_type = 'company'
        elif str(self.TipoClienteFE) == '02' or str(self.TipoClienteFE) == '04':
            self.tipoContribuyente = '1'
            self.company_type = 'person'
        else:
            self.tipoContribuyente = ''

    def _get_country_id(self):
        self._cr.execute(
            "SELECT id FROM res_country WHERE code LIKE 'PA' LIMIT 1")
        country_id = self._cr.fetchone()
        return country_id

    @api.onchange('province_id')
    def onchange_province_id(self):
        res = {}
        # self.fe_district_id=""
        # self.sector_id=""

        if self.province_id:
            self._cr.execute('SELECT electronic_invoice_district.id, electronic_invoice_district.name FROM electronic_invoice_district WHERE electronic_invoice_district.province_id = %s AND electronic_invoice_district.country_id = ( SELECT electronic_invoice_province.country_id FROM electronic_invoice_province WHERE electronic_invoice_province.id = %s) ', (self.province_id.id, self.province_id.id))
            districts = self._cr.fetchall()
            ids = []

            for district in districts:
                ids.append(district[0])
            res['domain'] = {'fe_district_id': [('id', 'in', ids)]}
        self.CodigoUbicacion = str(
            str(self.provincia) + "-" + str(self.distrito) + "-" + str(self.corregimiento))
        return res

    @api.onchange('fe_district_id')
    def onchange_fe_district_id(self):
        res = {}
        # self.sector_id=""
        if self.fe_district_id:
            self._cr.execute('SELECT electronic_invoice_sector.id, electronic_invoice_sector.name FROM electronic_invoice_sector WHERE electronic_invoice_sector.fe_district_id = %s AND  electronic_invoice_sector.country_id = ( SELECT electronic_invoice_district.country_id FROM electronic_invoice_district WHERE electronic_invoice_district.id = %s) ', (self.fe_district_id.id, self.fe_district_id.id))
            sectors = self._cr.fetchall()
            ids = []

            for sector in sectors:
                ids.append(sector[0])
            res['domain'] = {'sector_id': [('id', 'in', ids)]}
        self.CodigoUbicacion = str(
            str(self.provincia) + "-" + str(self.distrito) + "-" + str(self.corregimiento))
        return res

    @api.onchange('sector_id')
    def onchange_sector_id(self):
        self.CodigoUbicacion = str(
            str(self.provincia) + "-" + str(self.distrito) + "-" + str(self.corregimiento))

    @api.onchange('company_type')
    @api.depends('company_type')
    def _onchange_company_type(self):
        if self.company_type == 'person':
            logging.info(str(self.company_type))
            if self.TipoClienteFE in ('01', '03'):
                self.TipoClienteFE = '02'
        else:
            if self.TipoClienteFE in ('02', '04'):
                self.TipoClienteFE = '01'
    @api.onchange('company_type', 'name', 'email', 'phone', 'mobile')
    @api.depends('company_type', 'name', 'email', 'phone', 'mobile')
    def compute_active_fe(self):
        search_partner_mode = self.env.context.get('res_partner_search_mode')
        is_supplier = False
        if search_partner_mode:
            is_supplier = search_partner_mode == 'supplier'

        for partner in self:
            config_document_obj = self.env["electronic.invoice"].search(
                [('fe_company_config', '=', self.env.company.id)], limit=1)
            if config_document_obj and is_supplier == False:
                partner.is_company_config = True
            else:
                partner.is_company_config = False
                partner.TipoClienteFE = '00'

    @api.onchange('numeroRUC')
    @api.depends('numeroRUC')
    def update_vat(self):
        for partner in self:
            partner.vat = partner.numeroRUC
