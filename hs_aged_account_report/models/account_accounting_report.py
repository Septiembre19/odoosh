# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class AccountingReport(models.AbstractModel):
	_inherit = 'account.accounting.report'

	account_account_ids = fields.Many2many(
		comodel_name='account.account',
		relation='account_report_account_account_rel',
		column1='account_move_line_id',
		column2='account_account_id'
	)