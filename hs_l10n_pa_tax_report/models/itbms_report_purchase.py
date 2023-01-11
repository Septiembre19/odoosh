# -*- coding: utf-8 -*-

import copy, ast
from odoo.tools.misc import xlsxwriter
from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class ITBMSReportPurchase(models.Model):
	_inherit = "itbms.report"


	def template_line(self):
		if not self.report_type == 'purchase':
			return super(ITBMSReportPurchase, self).template_line()

		columns = [
			{'field': 'fecha', 'id': None, 'value': '', 'type': 'text'},
			{'field': 'name', 'id': None, 'value': '', 'type': 'text', 'colspan': 1},
			{'field': 'reference', 'id': None, 'value': '', 'type': 'text'}
		]

		for subline in self.line_ids:
			columns.append({
				'field': 'account_id', 'id': subline.account_id.id, 'type': 'dict', 'value': [
					{'field': 'debit', 'value': '', 'type': 'monetary'},
					{'field': 'credit', 'value': '', 'type': 'monetary'}
				]
			})
		
		return columns


	def set_header(self, options, sheet, styles):
		if not self.report_type == 'purchase':
			return super(ITBMSReportPurchase, self).set_header(options, sheet, styles)
		
		style_title = styles.get('title_A1')
		style_subtitle = styles.get('subtitle_A1')
		style_text_A3 = styles.get('text_A3')
		style_text_A4 = styles.get('text_A4')
		style_column_header = styles.get('table_column_header_A1')
			
		company = self.env.company
		month = options.get('month')
		year = options.get('year')
		sheet.merge_range(0, 0, 0, 12, "IMPORTACIONES DEL CASTILLO S.A.", style_title)
		sheet.merge_range(1, 0, 1, 12, "REPORTE ITBMS", style_subtitle)
		sheet.write(2, 6, year, style_subtitle)
			
		sheet.merge_range(3, 0, 3, 2, "CORRESPONDIENTE AL MES DE", style_text_A3)
		sheet.write(3, 3, month, style_text_A3)
		sheet.merge_range(4, 0, 4, 2, "INFORME DE COMPRAS", style_text_A4)
		sheet.merge_range(5, 0, 5, 2, company.name, style_text_A4)
		
		dt = self.get_orm_datetime()
		sheet.write(3, 10, 'FECHA', style_text_A3)
		sheet.write(4, 10, 'HORA', style_text_A3)
		sheet.write(3, 11, dt.get('date'), style_text_A3)
		sheet.write(4, 11, dt.get('time'), style_text_A3)

		sheet.merge_range(7, 0, 8, 0, 'FECHA', style_column_header)
		sheet.merge_range(7, 1, 8, 2, 'NOMBRE PROVEEDOR', style_column_header)
		sheet.merge_range(7, 3, 8, 3, 'REF FAC COMPRA', style_column_header)
		
		colpos = 4
		for subline in self.line_ids:
			sheet.merge_range(7, colpos, 7, colpos+1, subline.name, style_column_header)

			sheet.write(8, colpos, 'DEBITO', style_column_header)
			sheet.write(8, colpos+1, 'CREDITO', style_column_header)
			colpos += 2

		"""
		sheet.merge_range(7, 4, 7, 5, 'CUENTA POR PAGAR PROVEEDOR', style_column_header)
		sheet.merge_range(7, 6, 7, 7, 'PROVEEDOR CONTADO', style_column_header)
		sheet.merge_range(7, 8, 7, 9, 'CUENTA POR PAGAR ITBMS', style_column_header)
			
		sheet.write(8, 4, 'DEBITO', style_column_header)
		sheet.write(8, 5, 'CREDITO', style_column_header)
		sheet.write(8, 6, 'DEBITO', style_column_header)
		sheet.write(8, 7, 'CREDITO', style_column_header)
		sheet.write(8, 8, 'DEBITO', style_column_header)
		sheet.write(8, 9, 'CREDITO', style_column_header)
		"""

		sheet.set_column(0, 0, 12)
		sheet.set_column(1, 2, 15)
		sheet.set_column(3, 9, 13)
			
		sheet.set_column(10, 11, 12)



	def get_content(self, options):
		if not self.report_type == 'purchase':
			return super(ITBMSReportPurchase, self).get_content(options)
		
		date_start = options.get('date_start')
		date_end = options.get('date_end')
		# accounts = options.get('accounts')

		# account_ids = self.env['account.account'].browse(accounts)
		orm = [('invoice_date', '>=', date_start), ('invoice_date', '<=', date_end)]
		orm_filter = orm + ast.literal_eval(self.move_type_domain)
		invoices = self.env['account.move'].search(orm_filter, limit=100)
		report = []
		for move in invoices:
			row = [
				{'field': 'fecha', 'value': fields.Date.to_string(move.invoice_date), 'type': 'text'},
				{'field': 'name', 'value': str(move.name or ''), 'type': 'text', 'colspan': 1},
				{'field': 'reference', 'value': str(move.ref or ''), 'type': 'text'}
			]
			# for account in account_ids:
			for subline in self.line_ids:
				lines = move.line_ids.filtered(lambda l:l.account_id.id == subline.account_id.id)
				total_debit = sum(lines.mapped('debit') if lines else [0.00])
				total_credit = sum(lines.mapped('credit') if lines else [0.00])
				row.append({
					'field': 'account', 'type': 'dict', 'value': [
						{'field': 'debit', 'value': total_debit, 'type': 'monetary'},
						{'field': 'credit', 'value': total_credit, 'type': 'monetary'}
					]
				})
			report.append(row)
		"""
		report_length = len(report)
		if report_length < 10 and report_length > 0:
			current_line = report[0]
			old_line = copy.deepcopy(current_line)
			new_line = copy.deepcopy(current_line)
			template_row = self.write_line_empty(new_line)
			for report_line in range(0, 10 - report_length):
				report.append(template_row)
			report[0] = old_line
		return report
		"""
		report_length = len(report)
		if report_length < 10 and report_length >= 0:
			if report_length == 0:
				current_line = self.template_line()
			else:
				current_line = report[0]
			old_line = copy.deepcopy(current_line)
			new_line = copy.deepcopy(current_line)
			template_row = self.write_line_empty(new_line)
			for report_line in range(0, 10 - report_length):
				report.append(template_row)
			report[0] = old_line

		return report