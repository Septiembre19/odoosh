# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


import logging
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"

	change_price = fields.Boolean("change Price", compute="compute_change_price")

	
	def compute_change_price(self):
		for line in self:
			group_name = "hs_sale_price_control.group_manage_product_price_sale"
			group = self.env.ref(group_name)
			user = self.env.user
			if not user in group.users:
				line.change_price = False
			else:
				line.change_price = True