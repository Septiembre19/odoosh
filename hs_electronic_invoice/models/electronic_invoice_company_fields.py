# -*- coding: utf-8 -*-

from dataclasses import field
from email.policy import default
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime
import logging

class electronic_invoice_company_fields(models.Model):
	_inherit = "electronic.invoice"

	fe_principal_company_config = fields.Many2one("res.company", string="Compañia Principal", store=True)
	fe_company_config = fields.Many2one("res.company", string="Sucursal", store=True)
	is_sucursal = fields.Boolean(string="Sucursal", store=True)
# 	fe_company_config = fields.Char(
# 		string="Compañia",
# 		default=''
# )
	# asignar campos al modulo de res.company