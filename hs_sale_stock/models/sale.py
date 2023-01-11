# -*- coding: utf-8 -*-

import json
from multiprocessing import connection
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)



class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	alt_qty_available_str = fields.Char(compute='_compute_stock_advanced', string="Global Available Qty", compute_sudo=True)
	

	@api.depends('product_id', 'display_qty_widget')
	def _compute_stock_advanced(self):
		for line in self:
			content = []
			companies = self.env['res.company']
			filter_query = [('id', '!=', self.env.company.id)]
			for company in companies.search(filter_query):
				query_orm = [
					('id', '!=', line.product_id.id),
					('default_code', '=', line.product_id.default_code),
					('company_id', 'in', [False, company.id])
				]
				template_obj =self.env['product.template'] 
				product_alt_id = template_obj.search(query_orm, limit=1) 

				query_orm = [
					('on_hand', '=', True), 
					('quantity', '>=', 0), 
					('product_id', 'in', [line.product_id.id, product_alt_id.id]),
					('company_id', '=', company.id)
				]

				quants = self.env['stock.quant'].search(query_orm)
				quantity = sum(quants.mapped('quantity'))
				
				content.append({
					'company': company.name,
					'quantity': quantity
				})
			line.alt_qty_available_str = json.dumps(content)


	@api.onchange("product_id", "product_uom_qty")
	def _onchange_product(self):
		if self.product_uom_qty and self.product_id and not self.product_id.allow_negative_stock:
			# qty_available = self.free_qty_today
			qty_available = self.product_id.free_qty
			qty_require = self.product_uom_qty
			if qty_available < qty_require:
				message = ("La cantidad a vender es mayor que la disponible "
				"en inventario. {}/{}").format(qty_require, qty_available)
				raise UserError(message)