# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"

	order_name = fields.Char(string='Order Name', related="order_id.name")
	date_order = fields.Datetime(string="Order Date", related="order_id.date_order")
	partner_name_ext = fields.Char(string='Customer Ext.', related="order_id.partner_name_ext")
	invoice = fields.Many2one("account.move", "Invoice", compute="compute_invoice")
	no_fiscal = fields.Char("Ref. Fiscal", compute="compute_invoice")


	@api.depends('invoice_lines')
	def compute_invoice(self):
		for line in self:
			line.invoice = False
			line.no_fiscal = False
			
			invoice_lines = line.invoice_lines or []
			for inv_line in invoice_lines:
				line.invoice = inv_line.move_id
				line.no_fiscal = inv_line.move_id.numero_fiscal
				break