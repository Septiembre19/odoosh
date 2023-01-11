# -*- coding: utf-8 -*-

from collections import deque
from datetime import datetime
import io
import json

from odoo import http, fields
from odoo.http import request
from odoo.tools import ustr
from odoo.tools.misc import xlsxwriter
from odoo.addons.web.controllers.pivot import TableExporter

import logging
_logger = logging.getLogger(__name__)



class PivotController(TableExporter):

	
	@http.route('/web/pivot/export_xlsx', type='http', auth="user")
	def export_xlsx(self, data, token):
		jdata = json.loads(data)
		output = io.BytesIO()
		workbook = xlsxwriter.Workbook(output, {'in_memory': True})
		worksheet = workbook.add_worksheet(jdata['title'])

		header_bold = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#AAAAAA'})
		header_plain = workbook.add_format({'pattern': 1, 'bg_color': '#AAAAAA'})
		bold = workbook.add_format({'bold': True})

		measure_count = jdata['measure_count']
		origin_count = jdata['origin_count']

		# Step 1: writing col group headers
		col_group_headers = jdata['col_group_headers']


		# x,y: current coordinates
		# carry: queue containing cell information when a cell has a >= 2 height
		#      and the drawing code needs to add empty cells below
		x, y, carry = 1, 7, deque()
		for i, header_row in enumerate(col_group_headers):
			worksheet.write(i, 0, '', header_plain)
			for header in header_row:
				while (carry and carry[0]['x'] == x):
					cell = carry.popleft()
					for j in range(measure_count * (2 * origin_count - 1)):
						worksheet.write(y, x+j, '', header_plain)
					if cell['height'] > 1:
						carry.append({'x': x, 'height': cell['height'] - 1})
					x = x + measure_count * (2 * origin_count - 1)
				for j in range(header['width']):
					worksheet.write(y, x + j, header['title'] if j == 0 else '', header_plain)
				if header['height'] > 1:
					carry.append({'x': x, 'height': header['height'] - 1})
				x = x + header['width']
			while (carry and carry[0]['x'] == x):
				cell = carry.popleft()
				for j in range(measure_count * (2 * origin_count - 1)):
					worksheet.write(y, x+j, '', header_plain)
				if cell['height'] > 1:
					carry.append({'x': x, 'height': cell['height'] - 1})
				x = x + measure_count * (2 * origin_count - 1)
			x, y = 1, y + 1

		# Step 2: writing measure headers
		measure_headers = jdata['measure_headers']

		if measure_headers:
			worksheet.write(y, 0, '', header_plain)
			for measure in measure_headers:
				style = header_bold if measure['is_bold'] else header_plain
				worksheet.write(y, x, measure['title'], style)
				for i in range(1, 2 * origin_count - 1):
					worksheet.write(y, x+i, '', header_plain)
				x = x + (2 * origin_count - 1)
			x, y = 1, y + 1
			# set minimum width of cells to 16 which is around 88px
			worksheet.set_column(0, len(measure_headers), 16)

		# Step 3: writing origin headers
		origin_headers = jdata['origin_headers']

		if origin_headers:
			worksheet.write(y, 0, '', header_plain)
			for origin in origin_headers:
				style = header_bold if origin['is_bold'] else header_plain
				worksheet.write(y, x, origin['title'], style)
				x = x + 1
			y = y + 1

		# Step 4: writing data
		x = 0
		for row in jdata['rows']:
			worksheet.write(y, x, row['indent'] * '     ' + ustr(row['title']), header_plain)
			for cell in row['values']:
				x = x + 1
				if cell.get('is_bold', False):
					worksheet.write(y, x, cell['value'], bold)
				else:
					worksheet.write(y, x, cell['value'])
			x, y = 0, y + 1


		#========================================================
		# Seccion alterada para agregar el encabezado del reporte
		title_A1 = workbook.add_format({'font_size': 16, 'align': 'center', 'valign': 'vcenter'})
		title_A1.set_bg_color(False)

		subtitle_A1 = workbook.add_format({'font_size': 14, 'align': 'center', 'valign': 'vcenter'})
		subtitle_A1.set_bg_color(False)

		text_A3 = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'right', 'valign': 'vcenter'})
		subtitle_A1.set_bg_color(False)

		# date_obj = datetime.strptime(datetime.now(), '%Y-%m-%d')
		date_obj = datetime.now()
		year = date_obj.strftime("%Y")

		orm_dt = fields.Datetime.now()
		dt = fields.Datetime.context_timestamp(request, orm_dt)
		lang = request.env['res.lang'].search([('code', '=', request.env.lang)], limit=1)

		
		worksheet.merge_range(0, 0, 0, 12, "IMPORTACIONES DEL CASTILLO S.A.", title_A1)
		worksheet.merge_range(1, 0, 1, 12, jdata['title'], subtitle_A1)
		worksheet.write(2, 6, year, subtitle_A1)

		worksheet.merge_range(3, 2, 3, 3, "Compañía", text_A3)
		worksheet.merge_range(4, 2, 4, 3, request.env.company.name, text_A3)

		str_date = dt.strftime(lang.date_format)
		str_time = dt.strftime(lang.time_format)
		worksheet.write(3, 10, 'FECHA', text_A3)
		worksheet.write(4, 10, 'HORA', text_A3)
		worksheet.write(3, 11, str_date, text_A3)
		worksheet.write(4, 11, str_time, text_A3)


		workbook.close()
		xlsx_data = output.getvalue()
		response = request.make_response(xlsx_data,
			headers=[('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
					('Content-Disposition', 'attachment; filename=table.xlsx')],
			cookies={'fileToken': token})

		return response
