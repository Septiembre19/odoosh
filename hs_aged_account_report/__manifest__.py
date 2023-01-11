# -*- coding: utf-8 -*-

{
	'name': 'hs_aged_account_report',
	'summary': 'Ajustes - Reportes Contables',

	'description': """
- Sobreescribe el reporte.
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
	'depends': [
		'account_reports'
	],

	# any external library necessary for this one to work correctly
	'external_dependencies': {
		'python': [],
	},

	# always loaded
	'data': [
		'views/assets.xml',
		'views/search_template_view.xml',
	],
}