# -*- coding: utf-8 -*-

{
	'name': 'Panama - reportes itbms',
	'summary': '',

	'description': """
- Reporte de impuestos para gastos.
- Reporte de impuestos para ventas.
- Reporte de impuestos para compras.
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
	'depends': ['account'],

	# any external library necessary for this one to work correctly
	'external_dependencies': {
		'python': [],
	},

	# always loaded
	'data': [
		'security/ir.model.access.csv',
		'data/itbms_report.xml',
		'views/panama_tax_report_views.xml',
		'wizard/panama_tax_report_wizard_views.xml'
	],
}