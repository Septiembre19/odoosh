# -*- coding: utf-8 -*-

import base64
import json
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class PanamaTaxReportWizard(models.TransientModel):
	_name = 'panama.tax.report.wizard'
	_description = "Asistente reporte de impuestos"
	
	start_date = fields.Date(string='Start Date')
	end_date = fields.Date(string='End Date')
	itbms_report_id = fields.Many2one(comodel_name='itbms.report', string='Plantilla ITBMS')
	 


	def Confirm(self):
		"""
		report_type = self._context.get('report_type', False)
		report_name = self._context.get('report_name', False)
		report_type = report_type if report_type else 'sale'
		report_name = report_name if report_name else 'Informe ITBMS Facturacion'
		"""
		report_type = self.itbms_report_id.report_type
		report_name = self.itbms_report_id.name
		# accounts = self.itbms_report_id.account_ids.ids
		params = {
			'date_start': fields.Date.to_string(self.start_date),
			'date_end': fields.Date.to_string(self.end_date),
			#'report': report_type,
			#'name':report_name,
			'report': self.itbms_report_id.id,
			# 'accounts': accounts
		}
		content=base64.urlsafe_b64encode(json.dumps(params).encode())
		return {
			'type': 'ir.actions.act_url',
			'target': 'new',
			'url': '/report/ibtms?content=%s' % content.decode()
		}

class PTRWizardAccount(models.TransientModel):
	_name = 'panama.tax.report.wizard.accounts'
	_description = "Cuentas contables l10n_pa Report"

	wizard_id = fields.Many2one(comodel_name='panama.tax.report.wizard', string='Wizard')
	account_id = fields.Many2one('account.account', 'Account')
	
