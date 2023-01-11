# -*- coding: utf-8 -*-

import io
import locale
from datetime import datetime
from odoo.tools.misc import xlsxwriter
from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class ITBMSReport(models.Model):
	_name = "itbms.report"
	_description = "Reporte ITBMS"

	name = fields.Char(string='Report Name')
	move_type_domain = fields.Char(string='Move Types Domain')
	# account_ids = fields.Many2many(comodel_name='account.account', string='Account')
	report_type = fields.Selection(string='Report Type', selection=[
		('sale', 'Sale'), ('purchase', 'Purchase'), ('expense', 'Expense')
	],required=True)
	line_ids = fields.One2many(comodel_name='itbms.report.line', inverse_name='ibtms_report_id', string='Line Report')
	


	def _set_header(self, options, sheet, styles):
		date_str = options.get('date_start')
		date_obj = datetime.strptime(date_str, '%Y-%m-%d')
		options['month'] = date_obj.strftime("%B")
		options['year'] = date_obj.strftime("%Y")
		self.set_header(options, sheet, styles)


	def set_header(self, options, sheet, styles):
		return


	def get_content(self, options):
		return ""


	def set_cursor(self, row_position, col_position):
		pass


	def get_orm_datetime(self):
		orm_dt = fields.Datetime.now()
		dt = fields.Datetime.context_timestamp(self, orm_dt)
		lang = self.env['res.lang'].search([('code', '=', self.env.lang)], limit=1)
		return {
			'date': dt.strftime(lang.date_format),
			'time': dt.strftime(lang.time_format)
		}


	def write_cell(self, cell, sheet, rowpos, colpos, style):
		colspan = cell.get('colspan', 0)
		rowspan = cell.get('rowspan', 0)
		content = cell.get("value", False)
		if colspan > 0 or rowspan > 0:
			sheet.merge_range(rowpos, colpos, rowpos+rowspan, colpos+colspan, content, style)
			return colpos+colspan
		else:
			sheet.write(rowpos, colpos, content, style)
			return colpos
	

	def template_line(self):
		""" Metodo a sobreescribir para asignar el encabezado de la página
		"""
		return {}


	def write_line_empty(self, report_line):
		copy_line = report_line
		for cell in copy_line:
			if cell.get('type') != 'dict':
				cell['value'] = ''
			else:
				content = cell.get("value", False)
				cell['value'] = self.write_line_empty(content)
		return copy_line


	def write_line(self, report_line, sheet, row_pos, col_pos, styles):
		column = col_pos
		row = row_pos
		for cell in report_line:
			if cell.get("type", False) == 'text':
				style = styles.get('table_cell_text_A1', None)
				column = self.write_cell(cell, sheet, row, column, style)
				column = column + 1
			elif cell.get("type", False) == 'monetary':
				style = styles.get('table_cell_currency_A1', None)
				column = self.write_cell(cell, sheet, row, column, style)
				column = column + 1
			elif cell.get("type", False) == 'dict':
				content = cell.get("value", False)
				row, column = self.write_line(content, sheet, row, column, styles)
		return row, column

	
	def get_styles(self, workbook):
		title_A1 = workbook.add_format({'font_name': 'Calibri', 'font_size': 16, 'align': 'center', 'valign': 'vcenter'})
		subtitle_A1 = workbook.add_format({'font_name': 'Calibri', 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})
		text_A3 = workbook.add_format({'font_name': 'Calibri', 'font_size': 12, 'bold': False, 'align': 'right', 'valign': 'vcenter'})
		text_A4 = workbook.add_format({'font_name': 'Calibri', 'font_size': 12, 'bold': True, 'align': 'right', 'valign': 'vcenter'})
		column_header_A1 = workbook.add_format({'border': 1, 'font_name': 'Calibri', 'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
		cell_currency_A1 = workbook.add_format({'border': 1, 'num_format': '#,##0.00', 'align': 'right', 'valign': 'vcenter'})
		cell_text_A1 = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
		styles = {
			'title_A1': title_A1,
			'subtitle_A1': subtitle_A1,
			'text_A3': text_A3,
			'text_A4': text_A4,
			'table_column_header_A1': column_header_A1,
			'table_cell_currency_A1':cell_currency_A1,
			'table_cell_text_A1': cell_text_A1,
		}
		return styles


	def xlsx_report(self, options, sheet, styles):
		report = self.get_content(options)
		self._set_header(options, sheet, styles)
		row_pos = 9
		col_pos = 0
		for line in report:
			self.write_line(line, sheet, row_pos, col_pos, styles)
			col_pos = 0
			row_pos = row_pos + 1
		return row_pos, col_pos


	def get_report_itbms_xlsx(self, options):
		output = io.BytesIO()
		workbook = xlsxwriter.Workbook(output, {'in_memory': True})
		sheet = workbook.add_worksheet("informe")
		styles = self.get_styles(workbook)
		self.xlsx_report(options, sheet, styles)
		workbook.close()
		output.seek(0)
		generated_file = output.read()
		output.close()

		return generated_file


class ITBMSReportLine(models.Model):
	_name = "itbms.report.line"
	_description = "Linea de Reporte ITBMS"


	ibtms_report_id = fields.Many2one(comodel_name='itbms.report', string='Reporte ITBMS', required=True)
	account_id = fields.Many2one(comodel_name='account.account', string='Account', required=True)
	name = fields.Char(string='Title', required=True)
	position = fields.Integer(string='Column Position', default=1, required=True)