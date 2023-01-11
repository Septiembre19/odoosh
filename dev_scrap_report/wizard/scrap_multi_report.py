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


class ScrapMultiReport(models.TransientModel):
    _name = 'scrap.multi.report'

    scrap_ids = fields.Many2many('stock.scrap', string='Scraps')

    def print_scrap_report(self):
        active_ids = self._context.get('active_ids')
        scrap_ids = self.env['stock.scrap'].browse(active_ids)
        if scrap_ids:
            self.scrap_ids = [(6, 0, scrap_ids.ids)]
        return self.env.ref('dev_scrap_report.menu_multi_scrap_print').report_action(self)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
