# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Scrap Order Report',
    'version': '14.0.1.0',
    'sequence': 1,
    'category': 'Warehouse',
    'description':
        """
        This Module add below functionality into odoo

        1.Prints Scrap Products Report\n
        odoo app will add Scrap Report
Scrap Report 
Odoo scrap report 
Manage scrap report 
Odoo manage scrap report 
Odoo application allow authenticated users to print report of Scrap Orders
Only user with Allow to Print Scrap Report can print Scrap Order Report
Odoo Only user with Allow to Print Scrap Report can print Scrap Order Report
Print report of selected Scrap Orders
Odoo Print report of selected Scrap Orders
Print Scrap Order Report based on date range
Odoo Print Scrap Order Report based on date range
Manage Print Scrap Order Report based on date range
Odoo manage Print Scrap Order Report based on date range
Give right to the users for accessing this feature
Odoo Give right to the users for accessing this feature
Print report of selected Scrap Orders
odoo Print report of selected Scrap Orders
Scrap record 
Odoo scrap record
Manage scrap record 
Odoo manage scrap record 
Adjust date for scrap orders
Odoo adjust date for scrap orders

    """,
    'summary': 'odoo app print multiple Scrap order Report,Print product scrap order report based on scrap date, scrap order report date based,Inventory scrap report, product scrap order report, print scrap product detail,daily scrap order report',
    'depends': ['stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/template_scrap_date_range_views.xml',
        'report/template_multi_scrap_views.xml',
        'report/menu_scrap_date_range_views.xml',
        'report/menu_scrap_multi_views.xml',
        'wizard/scrap_date_range_views.xml',
        'wizard/scrap_multi_views.xml'
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':12.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
