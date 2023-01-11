from odoo import api, fields, models, _

class AccountInvoice(models.Model):
	_inherit = "account.move"

	partner_name_ext = fields.Char("A nombre de", help=_("Nombre auxiliar del cliente "
		"cuando la factura esta asignada al cliente contado")
	)
	
	# custom_payment_method = fields.Many2one('account.journal', domain=[('type', 'in', ('bank', 'cash'))], string="Tipo de pago", help='Especifíque el método de pago.') #, ('company_id', '=', company_id)
	custom_payment_method = fields.Selection(
		string='Tipo de pago',
		selection=[
			('ACH', 'ACH'),
			('Cheque', 'Cheque'),
			('Efectivo', 'Efectivo'),
			('visa', 'T/C Visa'),
			('clave', 'Clave'),
		],
		# compute="_compute_tipo", # default='',
		help='Especifíque el método de pago.'
		)
		
	numero_fiscal = fields.Char(string='Número Fiscal', copy=False)
	