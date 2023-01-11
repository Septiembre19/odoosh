# -*- coding: utf-8 -*-

{
	'name': "Partner Separator",

	'summary': """Partner Rank - Separator""",

	'description': """
		- Realiza la separacion del recurso Partner en base a cliente o proveedor.
	""",

	'author': "HS Consulting",
	'website': "https://www.hconsul.com/odoo",
	'maintainer': 'HS Consulting S.A.',

	'contributors': [
		'Luis Dominguez',
	],

	'category': 'Technical',
	'version': '15.0.1.0.0',
	'license': 'OPL-1',

	'depends': ['base'],

	'external_dependencies': {
		'python': [],
	},

	'data': [
		'views/res_partner_views.xml',
	],
	
}