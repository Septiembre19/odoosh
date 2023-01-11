# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

import logging
import json
_logger = logging.getLogger(__name__)


class anexo72Report(models.AbstractModel):
	_name = "account.anexo72.report"
	_description = "Reporte Anexo 72"
	_inherit = "account.report"

	# filter_date = {'date_from': '', 'date_to': '', 'filter': 'today'}
	filter_date = {'mode': 'range', 'filter': 'today'}
	filter_all_entries = False
	filter_journals = None
	filter_analytic = None
	filter_unfold_all = None


	def _get_columns_name(self, options):
		"""[summary]
		
		Arguments:
			options {[type]} -- [description]
		
		Returns:
			[type] -- [description]
		"""
		return [{'name': ''},
				{'name': _("TIPO DE PERSONA")},
				{'name': _("RUC")},
				{'name': _("DV")},
				{'name': _("NOMBRE O RAZÓN SOCIAL")},
				{'name': _("TIPO DE PAGO"), 'class': 'number'},
				{'name': _("CONCEPTO"),'class': 'number'},
				{'name': _("MONTO"),'class': 'number'},
				{'name': _("APLICACIÓN"), 'class': 'number'}]

	@api.model
	def _get_report_name(self):
		return _('Reporte Anexo 72')
	
	@api.model
	def _get_lines(self, options, line_id=None):
		invoices = self._do_query(options)
		count = 1
		lines = []

		for invoice in invoices:
			invoice = list(invoice)
			# invoice[7] = self.format_value(invoice[7])
			#logging.info(str(invoice))
			lines.append({
				'id': count,
				'name': count,
				'unfoldable': False,
				'level': 3,
				'columns': [{'name' : v} for v in invoice],
			})
			count+=1

		if len(invoices) == 0:
			lines.append({
				'id': '',
				'name': '',
				'unfoldable': False,
				'level': 3,
				'columns': [{'name' : v} for v in ['', '', '', '', '', '', '', '',]],
			})
		return lines



	def _do_query(self,options):
		dt_from = options['date'].get('date_from')
		dt_to = options['date'].get('date_to')
		
		query = """
		select proveedor.tipo_persona, 
		proveedor.vat,
		proveedor.dv,
		proveedor.name,
		invoice.tipo_pago,
		detalle.concepto_72, 
		sum(detalle.price_subtotal),
		invoice.periodo
		from account_move_line As detalle , account_move as invoice, res_partner as proveedor
		where (detalle.date BETWEEN '{}' AND '{}') and detalle.move_id = invoice.id and invoice.partner_id = proveedor.id and invoice.state <> 'draft'
		and detalle.exclude_from_invoice_tab = 'f' and detalle.display_type is null and detalle.concepto_72 <> ''
		group by proveedor.tipo_persona, proveedor.vat,proveedor.dv,proveedor.name,invoice.tipo_pago,detalle.concepto_72,invoice.periodo;
		""".format(dt_from, dt_to)
		# format(dt_from, dt_to)
		# (detalle.date BETWEEN '{}' AND '{}')

		self.env.cr.execute(query)
		results = self.env.cr.fetchall()
		return results
		