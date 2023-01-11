# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

class purchaseOrderInherit1 (models.Model):
    # _name= 'manage.chofer'
    # _description = 'Modulo para administrar Chofer'
    _inherit = 'purchase.order'
   
    concepto = fields.Selection([
        ('1', 'Compras o adquisiciones de bienes muebles'),
        ('2', 'Servicios Básicos'),
        ('3', 'Honorarios y Comisiones por Servicios Personales'),
        ('4', 'Alquileres por Arrendamientos Comerciales'),
        ('5', 'Cargos Bancarios, Intereses y otros Gastos Financieros'),
        ('6', 'Compras o Servicios del Exterior'),
        ('7', 'Compras o Servicios Consolidados'),],string = 'Concepto', default='1', required=True)

    tipo_compra = fields.Selection([
        ('1l', 'Locales'),
        ('2l', 'Importaciones')], string='Compras Bienes y Servicios', default='1l', required=True)
    
	# type = fields.Selection([
    #     ('consu', 'Consumable'),
    #     ('service', 'Service')], string='Product Type', default='consu', required=True,
    #     help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
    #          'A consumable product is a product for which stock is not managed.\n'
    #          'A service is a non-material product you provide.')