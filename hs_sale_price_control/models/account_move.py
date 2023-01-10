# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


import logging
_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
	_inherit = "account.move.line"

	manage_price = fields.Boolean("Manage Price", compute="compute_manage_price")


	@api.depends('move_id.move_type')
	def compute_manage_price(self):
		for line in self:
			invoice = line.move_id
			if not invoice.move_type in ['out_invoice', 'out_refund']:
				line.manage_price = True
				return

			group_name = "hs_sale_price_control.group_manage_product_price_sale"
			group = self.env.ref(group_name)
			user = self.env.user
			if not user in group.users:
				line.manage_price = False
			else:
				line.manage_price = True