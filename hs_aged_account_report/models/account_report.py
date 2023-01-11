

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class AccountReport(models.AbstractModel):
	_inherit = 'account.report'
	
	filter_account_account = None

	@api.model
	def _init_filter_account_account(self, options, previous_options=None):
		if not self.filter_account_account:
			return
		
		previous_accounts = (previous_options or {}).get('account_account_ids', [])
		selected_account_ids = [int(account) for account in previous_accounts]
		selected_accounts = self.env['account.account'].search([('id', 'in', selected_account_ids)])
		options['account_account_ids'] = selected_accounts.ids
		options['selected_account_account_names'] = selected_accounts.mapped('name')

	
	@api.model
	def _get_options(self, previous_options=None):
		super(AccountReport, self)._get_options(previous_options=previous_options)
		options = {
			'unfolded_lines': previous_options and previous_options.get('unfolded_lines') or [],
		}

		# Multi-company is there for security purpose and can't be disabled by a filter.
		if self.filter_multi_company:
			if self._context.get('allowed_company_ids'):
				# Retrieve the companies through the multi-companies widget.
				companies = self.env['res.company'].browse(self._context['allowed_company_ids'])
			else:
				# When called from testing files, 'allowed_company_ids' is missing.
				# Then, give access to all user's companies.
				companies = self.env.companies
			if len(companies) > 1:
				options['multi_company'] = [
					{'id': c.id, 'name': c.name} for c in companies
				]

		# Call _init_filter_date/_init_filter_comparison because the second one must be called after the first one.
		if self.filter_date:
			self._init_filter_date(options, previous_options=previous_options)
		if self.filter_comparison:
			self._init_filter_comparison(options, previous_options=previous_options)
		if self.filter_analytic:
			options['analytic'] = self.filter_analytic
		if self.filter_account_account:
			domain_accounts = self.env['account.account'].search([('user_type_id', 'in', [
				self.env.ref('account.data_account_type_receivable').id, 
				self.env.ref('account.data_account_type_payable').id
			])])
			options['domain_account_ids'] = domain_accounts.ids
			options['account_account'] = self.filter_account_account

		filter_list = [attr
					   for attr in dir(self)
					   if (attr.startswith('filter_') or attr.startswith('order_'))
					   and attr not in ('filter_date', 'filter_comparison', 'filter_multi_company')
					   and len(attr) > 7
					   and not callable(getattr(self, attr))]
		for filter_key in filter_list:
			options_key = filter_key[7:]
			init_func = getattr(self, '_init_%s' % filter_key, None)
			if init_func:
				init_func(options, previous_options=previous_options)
			else:
				filter_opt = getattr(self, filter_key, None)
				if filter_opt is not None:
					if previous_options and options_key in previous_options:
						options[options_key] = previous_options[options_key]
					else:
						options[options_key] = filter_opt
		return options


	def _set_context(self, options):
		ctx = super(AccountReport, self)._set_context(options)
		if options.get('account_account_ids'):
			ctx['account_account_ids'] = self.env['account.account'].browse([int(t) for t in options['account_account_ids']])
		return ctx