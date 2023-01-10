# -*- coding: utf-8 -*-

{
	'name': "HS Desarrollos",

	'summary': """Ajustes Generales""",

	'description': """
		- control de Precios por grupo 
	""",

	'author': "HS Consulting S.A.",
	'website': "https://www.hconsul.com/",
	'maintainer': 'HS Consulting S.A.',

	'contributors': [
		'Luis Dominguez',
	],
	'category': 'Technical',
	'version': '1.0',
	'license': 'OPL-1',

	# any module necessary for this one to work correctly
	'depends': ['base', 'account', 'sale'],

	# any external library necessary for this one to work correctly
	'external_dependencies': {
		'python': [],
	},

	# always loaded
	'data': [
		'security/res_group.xml',
		'views/account_move_views.xml',
		'views/sale_order_views.xml'
	],
	# 'installable': True,
	'auto_install': False,
	'application': False,
}