# -*- coding: utf-8 -*-

{
	'name': "Ajustes Generales",

	'summary': """
	""",

	'description': """
- Ajustes para agregar un campo nombre de cliente contado.
- Renombrar texto nombre comercial por vendedor.
- Controlar boton delivery en ventas mediante un nuevo permiso.
- Ocultar boton Confirmar en Sales Order.
- Agrega campo NumeroFiscal a facturación
	""",

	'author': "HS Consulting S.A.",
	'website': "https://www.hconsul.com/",
	'maintainer': 'HS Consulting S.A.',

	'contributors': [
		'Ceila Hernandez',
		'Sleather Vega',
	],
	'category': 'Technical',
	'version': '1.0',
	'license': 'OPL-1',

	# any module necessary for this one to work correctly
	'depends': ['stock', 'account_accountant', "sale_management"],

	# any external library necessary for this one to work correctly
	'external_dependencies': {
		'python': [],
	},

	# always loaded
	'data': [
		'data/res_partner.xml',
		# 'security/ir.model.access.csv',
		'security/sale_security.xml',
		'views/account_move_view.xml',
		'views/sale_order_view.xml',
		'views/product_views.xml',
		'report/invoice_template.xml',
		'report/sale_order_template.xml',
		'views/stock_move_views.xml',
	],
	# 'installable': True,
	'auto_install': False,
	'application': False,
}