# -*- coding: utf-8 -*-

from tokenize import String
from odoo import models, fields, api, exceptions


class accountMoveInherit2(models.Model):
	_inherit = "account.move"


	# move_type = fields.Char(related="account_move.move_type")
	#AQUI IRAN LOS CAMPOS HEREDADOS DE PROVEEDORES PARA INFORME 43 / ANEXO 72 Y 94
	hs_tipo = fields.Selection(string= "Tipo Persona", related='partner_id.tipo_persona', readonly=True)
	hs_ruc = fields.Char(string="RUC", related='partner_id.vat')
	hs_dv = fields.Char(string="DV", related='partner_id.dv')

	#-------PARA INFORME 43-------
	concepto = fields.Selection([
	 	('1', 'Compras o adquisiciones de bienes muebles'),
	 	('2', 'Servicios Básicos'),
	 	('3', 'Honorarios y Comisiones por Servicios Personales'),
		('4', 'Alquileres por Arrendamientos Comerciales'),
		('5', 'Cargos Bancarios, Intereses y otros Gastos Financieros'),
		('6', 'Compras o Servicios del Exterior'),
		('7', 'Compras o Servicios Consolidados')], string = 'Concepto', help='Campo para concepto usado en Informe 43')

	compra = fields.Selection([
	 	('1', 'Locales'),
	 	('2', 'Importaciones')], string='Tipo de Compra', help='Campo para Tipo de compra usado en Informe 43')
	# concepto = fields.Selection(string= "Concepto", related='invoice_line_ids.hs_concepto')
	# compra = fields.Selection(string='Tipo de Compra', related='invoice_line_ids.hs_compra')

	#----------CAMPOS PARA INFORME 72------------
	tipo_pago = fields.Selection([
		('1', '1-Costos'),
		('2', '2-Gastos')], string='Tipo de Pago 72 y 94', help='Campo usado para Anexo 72 y 94')
	
	
	periodo = fields.Selection([
		('1', '1-Actual Pagado'),
		('2', '2-Actual por Pagar')], string='Período de Aplicación 72 y 94', help='Campo usado para Anexo 72 y 94')



class accountMoveLineInherit2(models.Model):
	_inherit = "account.move.line"

	#-------- CAMPOS para ANEXO 72 Y 94----------------
	concepto_72 = fields.Selection([
		('1', 'Mantenimiento'),
		('2', 'Elect., Agua y Tel.(Costo)'),
		('3', 'Dietas'),
		('4', 'Alquileres'),
		('5', 'Honorarios por Serv. Prof. y Comis.'),
		('6', 'Elect., Agua Y Tel. (Gasto)'),
		('7', 'Seguros (Gasto)'),
		('8', 'Transporte'),
		('9', 'Gastos de Representación'),
		('10', 'Seguro (Costos)'),
		('11', 'Gastos de Factoring')], string= "Concepto anexo 72")
	
	concepto_94 = fields.Integer(string= "Concepto anexo 94")

	move_type = fields.Selection(related='move_id.move_type', string="Move Type")
	
	#PRUEBA DE CALCULAR EL CONCEPTO A VER QUE ME SALE
	""" @api.depends('hconcep')
	def _compute_sum_monto(self):
		for invoice_line_ids in self:
			if invoice_line_ids.hconcep == 6:
				invoice_line_ids.monto += invoice_line_ids.price_subtotal  """
	

