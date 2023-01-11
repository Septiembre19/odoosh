from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
	_inherit = "stock.move.line"

	partner_id = fields.Many2one(comodel_name='res.partner', string='Contacto', compute="_compute_origin", store=True)
	partner_name = fields.Char(string='Referencia Contacto', compute="_compute_origin", store=True)
	operation = fields.Char(string='Operacion', compute="_compute_origin", store=True)
	purchase_id = fields.Many2one(comodel_name='purchase.order', string='Orden de Compra', compute="_compute_origin", store=True)
	sale_id = fields.Many2one(comodel_name='sale.order', string='Orden de Venta', compute="_compute_origin", store=True)
	account_move_id = fields.Many2one(comodel_name='account.move', string='Asiento Contable', compute="_compute_origin", store=True)
	account_move = fields.Char(string='Referencia Contable', compute="_compute_origin")
	
	@api.depends("move_id")
	def _compute_origin(self):
		try:
			generic_customer = self.env.ref('hs_dev_custom.generic_customer').id
		except:
			generic_customer = False
		for line in self:
			move_id = line.move_id
			
			line.partner_id = False
			line.partner_name = False
			line.purchase_id = False
			line.sale_id = False
			line.account_move_id = False
			line.account_move = False

			operation = move_id.picking_type_id.code
			if move_id.purchase_line_id:
				line.operation = "Compra" if operation == "incoming" else "Devolución"
				line.purchase_id = move_id.purchase_line_id.order_id
				if move_id.purchase_line_id.invoice_lines:
					invoices = move_id.purchase_line_id.invoice_lines
					line.account_move = invoices[0].move_id.name
					line.account_move_id = invoices[0].move_id
				partner_id = line.purchase_id.partner_id or move_id.partner_id
				line.partner_id = partner_id or False
				line.partner_name = partner_id.name if partner_id else False
			elif move_id.sale_line_id:
				line.operation = "Venta" if operation == "outgoing" else "Nota Credito"
				line.sale_id = move_id.sale_line_id.order_id
				if move_id.sale_line_id.invoice_lines:
					invoices = move_id.sale_line_id.invoice_lines
					line.account_move = invoices[0].move_id.name
					line.account_move_id = invoices[0].move_id
				partner_id = line.sale_id.partner_id or move_id.partner_id
				line.partner_id = partner_id or False
				if partner_id and partner_id.id == generic_customer:
					customer = line.sale_id.partner_name_ext or "No detallado"
					line.partner_name = "[%s]%s" % (partner_id.name, customer)
				else:
					line.partner_name = partner_id.name if partner_id else False
			else:
				line.operation = "Oper. Interna"
				partner_id = move_id.partner_id or move_id.company_id.partner_id
				line.partner_id = partner_id or False
				line.partner_name = partner_id.name if partner_id else False

				"""
				if move_id.inventory_id and move_id.inventory_id.move_ids:
					invoice = self.env["account.move"].search([('stock_move_id', '=', move_id.id)], limit=1)
					line.account_move = invoice.name
					line.account_move_id = invoice
				"""
				account_move = self.env["account.move"].search([('stock_move_id', '=', move_id.id)], limit=1)
				if account_move:
					line.account_move = account_move.name
					line.account_move_id = account_move
