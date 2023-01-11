# -*- coding: utf-8 -*-

import copy, ast
from odoo.tools.misc import xlsxwriter
from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class ITBMSReportSale(models.Model):
	_inherit = "itbms.report"


	def template_line(self):
		if not self.report_type == 'sale':
			return super(ITBMSReportSale, self).template_line()

		columns = [
			{'field': 'invoice_date', 'id': None, 'value': '', 'type': 'text'},
			{'field': 'name', 'id': None, 'value': '', 'type': 'text', 'colspan': 1},
			{'field': 'numero_fiscal', 'id': None, 'value': '', 'type': 'text'}
		]

		"""
		for account in self.account_ids:
			columns.append({
				'field': 'account_id', 'id': account.id, 'type': 'dict', 'value': [
					{'field': 'debit', 'value': '', 'type': 'monetary'},
					{'field': 'credit', 'value': '', 'type': 'monetary'}
				]
			})
		"""
		for subline in self.line_ids:
			columns.append({
				'field': 'account_id', 'id': subline.account_id.id, 'type': 'dict', 'value': [
					{'field': 'debit', 'value': '', 'type': 'monetary'},
					{'field': 'credit', 'value': '', 'type': 'monetary'}
				]
			})
		
		return columns


	def set_header(self, options, sheet, styles):
		if not self.report_type == 'sale':
			return super(ITBMSReportSale, self).set_header(options, sheet, styles)

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
		sheet.merge_range(4, 0, 4, 2, "INFORME DE FACTURACION", style_text_A4)
		sheet.merge_range(5, 0, 5, 2, company.name, style_text_A4)
		
		dt = self.get_orm_datetime()
		sheet.write(3, 10, 'FECHA', style_text_A3)
		sheet.write(4, 10, 'HORA', style_text_A3)
		sheet.write(3, 11, dt.get('date'), style_text_A3)
		sheet.write(4, 11, dt.get('time'), style_text_A3)

		sheet.merge_range(7, 0, 8, 0, 'FECHA', style_column_header)
		sheet.merge_range(7, 1, 8, 2, 'NOMBRE CLIENTE', style_column_header)
		sheet.merge_range(7, 3, 8, 3, 'NO. FISCAL', style_column_header)
		
		colpos = 4
		for subline in self.line_ids:
			sheet.merge_range(7, colpos, 7, colpos+1, subline.name, style_column_header)
			sheet.write(8, colpos, 'DEBITO', style_column_header)
			sheet.write(8, colpos+1, 'CREDITO', style_column_header)
			colpos += 2
		
		"""
		sheet.merge_range(7, 4, 7, 5, 'CUENTA ITBMS x PAGAR', style_column_header)
		sheet.merge_range(7, 6, 7, 7, 'CUENTA GRAVADA', style_column_header)
		sheet.merge_range(7, 8, 7, 9, 'CUENTA EXENTA', style_column_header)
			
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


	def get_content(self, options):
		if not self.report_type == 'sale':
			return super(ITBMSReportSale, self).get_content(options)

		date_start = options.get('date_start')
		date_end = options.get('date_end')
		# accounts = options.get('accounts')

		# account_ids = self.env['account.account'].browse(accounts)
		# account_ids = self.account_ids
		orm = [('invoice_date', '>=', date_start), ('invoice_date', '<=', date_end)]
		orm_filter = orm + ast.literal_eval("[('move_type', '=', 'out_invoice')]")
		invoices = self.env['account.move'].search(orm_filter)
		report = []
		for move in invoices:
			row = [
				{'field': 'fecha', 'value': fields.Date.to_string(move.invoice_date), 'type': 'text'},
				{'field': 'name', 'value': str(move.name or ''), 'type': 'text', 'colspan': 1},
				{'field': 'fiscal', 'value': str(move.numero_fiscal or ''), 'type': 'text'}
			]
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


	def xlsx_report(self, options, sheet, styles):
		row_pos, col_pos = super(ITBMSReportSale, self).xlsx_report(options, sheet, styles)
		if not self.report_type == 'sale':
			return row_pos, col_pos

		row_pos, col_pos = self.set_refund_header(sheet, styles, row_pos, col_pos)
		
		report = self.get_refund_content(options)
		for line in report:
			self.write_line(line, sheet, row_pos, col_pos, styles)
			col_pos = 0
			row_pos = row_pos + 1
		return row_pos, col_pos


	def set_refund_header(self, sheet, styles, row_pos=0, col_pos=0):
		style_text_A4 = styles.get('text_A4')
		style_column_header = styles.get('table_column_header_A1')

		company = self.env.company
		row = row_pos + 2
		col = col_pos
		sheet.merge_range(row, 0, row, 2, "INFORME DE NOTA CREDITO", style_text_A4)
		
		row += 1
		sheet.merge_range(row, 0, row, 2, company.name, style_text_A4)

		row += 2
		sheet.merge_range(row, 0, row+1, 0, 'FECHA', style_column_header)
		sheet.merge_range(row, 1, row+1, 2, 'NOMBRE CLIENTE', style_column_header)
		sheet.merge_range(row, 3, row+1, 3, 'NO. FISCAL', style_column_header)
		
		colpos = 4
		for subline in self.line_ids:
			sheet.merge_range(row, colpos, row, colpos+1, subline.name, style_column_header)

			sheet.write(row+1, colpos, 'DEBITO', style_column_header)
			sheet.write(row+1, colpos+1, 'CREDITO', style_column_header)
			colpos += 2

		row += 1
		"""
		sheet.merge_range(row, 4, row, 5, 'CUENTA ITBMS x PAGAR', style_column_header)
		sheet.merge_range(row, 6, row, 7, 'CUENTA GRAVADA', style_column_header)
		sheet.merge_range(row, 8, row, 9, 'CUENTA EXENTA', style_column_header)
		
		row += 1
		sheet.write(row, 4, 'DEBITO', style_column_header)
		sheet.write(row, 5, 'CREDITO', style_column_header)
		sheet.write(row, 6, 'DEBITO', style_column_header)
		sheet.write(row, 7, 'CREDITO', style_column_header)
		sheet.write(row, 8, 'DEBITO', style_column_header)
		sheet.write(row, 9, 'CREDITO', style_column_header)
		"""

		return row + 1, col
		
	
	def get_refund_content(self, options):
		date_start = options.get('date_start')
		date_end = options.get('date_end')
		
		orm = [('invoice_date', '>=', date_start), ('invoice_date', '<=', date_end)]
		orm_filter = orm + ast.literal_eval("[('move_type', '=', 'out_refund')]")
		invoices = self.env['account.move'].search(orm_filter)
		
		report = []
		for move in invoices:
			row = [
				{'field': 'fecha', 'value': fields.Date.to_string(move.invoice_date), 'type': 'text'},
				{'field': 'name', 'value': str(move.name or ''), 'type': 'text', 'colspan': 1},
				{'field': 'fiscal', 'value': str(move.numero_fiscal or ''), 'type': 'text'}
			]
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