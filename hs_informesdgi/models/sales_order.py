# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class salesOrderInherit7(models.Model):
	_inherit = "sale.order"

	#AQUI IRAN LOS CAMPOS HEREDADOS PARA LAS COTIZACIONES
	tax_venta = fields.Monetary(compute='_compute_tax_venta',string='Impuesto 7%', store=True)

	@api.depends('amount_tax')
	def _compute_tax_venta(self):
		for record in self:
			record.tax_venta = record.amount_tax * 2.0

