from odoo import api, fields, models, _

class AccountInvoice(models.Model):
	_inherit = "sale.order"

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
		
	hide_button_confirm = fields.Boolean(string='Only Quotations', compute="compute_hide_button_confirm")


	def compute_hide_button_confirm(self):
		for line in self:
			group_name = "hs_dev_custom.sale_quotation_only_users"
			group = self.env.ref(group_name)
			user = self.env.user
			if not user in group.users:
				line.hide_button_confirm = False
			else:
				line.hide_button_confirm = True
	