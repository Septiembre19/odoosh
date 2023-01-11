# -*- coding: utf-8 -*-

{
	'name': 'Sale Report',
	'summary': '',

	'description': """
- Reporte de productos.
	""",

	'author': "HS Consulting S.A.",
	'website': "https://www.hconsul.com/",
	'maintainer': 'HS Consulting S.A.',

	'contributors': [
		'Luis Dominguez',
	],
	'category': 'Technical',
	'version': '14.0.1.0.1',
	'license': 'OPL-1',

	# any module necessary for this one to work correctly
	'depends': ['base', 'account', 'sale', 'hs_dev_custom'],

	# any external library necessary for this one to work correctly
	'external_dependencies': {
		'python': [],
	},

	# always loaded
	'data': [
		'views/sale_report_views.xml',
	],
}