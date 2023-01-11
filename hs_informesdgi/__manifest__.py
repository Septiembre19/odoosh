# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Informe 43 / Anexo 72 y 94',
    'summary':'Crear nuevos campos para informes de compras/costos/gastos DGI',
    'description': """
        Es un módulo para agregar nuevos campos para los informes requeridos para DGI.
    """,
    'author': 'Hermec Consulting, S.A.',
    'maintainer':'Ceila Hernandez',
    "website": "https://www.hconsul.com/odoo",
    "category": "Accounting",
    "version": "14.0.3",
    "licence": "HCPL-1",
    'depends': ['account', 'account_reports'],
    'data': [
      # 'security/ir.model.access.csv',
      'views/account_move_inherit_view.xml',
      # 'views/purchase_order_view.xml',
      'views/res_partner_view.xml',
      # 'views/sales_order_view.xml',
      'reports/anexo_72_view.xml',
      'reports/anexo_94_view.xml',
     
    ],
    
    'installable': True,
    'auto_install': False,
}
