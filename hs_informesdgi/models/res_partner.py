# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import logging
_logger = logging.getLogger(__name__)

class resPartnerInherit2(models.Model):
	_inherit = "res.partner"

	tipo_persona = fields.Selection([
		('N', 'Natural'),
		('J', 'Jurídico'),
		('E', 'Extranjero'),], string='Tipo de Persona')

	dv = fields.Char(string="DV")
	
	
	
	