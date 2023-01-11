# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import api, models
from datetime import datetime
from odoo.tools import pytz


class ScrapMulti(models.AbstractModel):
    _name = 'report.dev_scrap_report.template_multi_scrap'

    def timezone_conversion(self, date):
        input_date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
        user = self.env.user
        tz = pytz.timezone(user.tz) or pytz.utc
        user_tz_date = pytz.utc.localize(input_date).astimezone(tz)
        date_without_tz = user_tz_date.replace(tzinfo=None)
        return date_without_tz

    def get_scrap_data(self, scrap_ids):
        data = []
        if scrap_ids:
            for scrap in scrap_ids:
                scrap_date = ''
                if scrap.date_done:
                    scrap_date = self.timezone_conversion(scrap.date_done)
                data.append({'number': scrap.name,
                             'product': scrap.product_id and scrap.product_id.name or '',
                             'qty': scrap.scrap_qty,
                             'location': scrap.location_id and scrap.location_id.name or '',
                             'scrap_location': scrap.scrap_location_id and scrap.scrap_location_id.name or '',
                             'scrap_date': scrap_date,
                             'state': scrap.state
                             })
        return data

    def _get_report_values(self, docids, data=None):
        docs = self.env['scrap.multi.report'].browse(docids)
        return {'doc_ids': docids,
                'doc_model': 'scrap.multi.report',
                'docs': docs,
                'timezone_conversion': self.timezone_conversion,
                'get_scrap_data': self.get_scrap_data
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
