# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api


class ScrapDateRangeReport(models.TransientModel):
    _name = 'scrap.date.range.report'

    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)

    def print_scrap_report(self):
        return self.env.ref('dev_scrap_report.menu_scrap_date_range_report').report_action(self)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
