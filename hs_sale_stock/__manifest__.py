# -*- coding: utf-8 -*-

{
	'name': 'hs_sale_stock',
	'summary': 'Ajustes - Sales & Stock',

	'description': """
- Bloquea la venta negativa de productos en ventas.
- Muestra la cantidad disponible en inventario de las otras bodegas.
	""",

	'author': "HS Consulting S.A.",
	'website': "https://www.hconsul.com/",
	'maintainer': 'HS Consulting S.A.',

	'contributors': [
		'Luis Dominguez',
	],
	'category': 'Technical',
	'version': '14.0.1.0.2',
	'license': 'OPL-1',

	# any module necessary for this one to work correctly
	'depends': ['sale_stock', 'stock_no_negative'],

	# any external library necessary for this one to work correctly
	'external_dependencies': {
		'python': [],
	},

	# always loaded
	'data': [
		'views/sale_order_views.xml'
	],

	'qweb': [
		# 'static/src/xml/sale_stock.xml',
	],
}