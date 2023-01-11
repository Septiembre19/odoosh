# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import base64
from odoo.http import Controller, route, request, content_disposition
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.tools import html_escape


import logging
_logger = logging.getLogger(__name__)


class ITBMSReportControllers(Controller):
	
	@route('/report/ibtms', type='http', auth='user', methods=['GET'], csrf=False)
	def get_report_itbms(self, content, **kw):
		_logger.info(content)
		
		uid = request.session.uid
		options = base64.urlsafe_b64decode(content.encode())
		options = json.loads(options.decode())
		account_report_model = request.env['account.report']
		cids = request.httprequest.cookies.get('cids', str(request.env.user.company_id.id))
		allowed_company_ids = [int(cid) for cid in cids.split(',')]
		report_obj = request.env["itbms.report"].with_user(uid).with_context(allowed_company_ids=allowed_company_ids)
		report_tmpl = report_obj.browse(options.get('report'))
		report_name = report_tmpl.name 
		try:
			response = request.make_response(
				None,
				headers=[
					('Content-Type', account_report_model.get_export_mime_type('xlsx')),
					('Content-Disposition', content_disposition(report_name + '.xlsx'))
				]
			)
			response.stream.write(report_tmpl.get_report_itbms_xlsx(options))
			# response.set_cookie('fileToken', token)
			return response
		except Exception as e:
			se = _serialize_exception(e)
			error = {
				'code': 200,
				'message': 'Odoo Server Error',
				'data': se
			}
			return request.make_response(html_escape(json.dumps(error)))
