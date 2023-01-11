# -*- coding: utf-8 -*-logging

import base64
from cmath import log
from io import BytesIO
from pydoc import cli
from odoo import models, fields, api, _
import zeep
import logging
from base64 import b64decode
from datetime import datetime, timezone
from odoo import http
from odoo.http import request
from odoo.http import content_disposition
import qrcode
from odoo.exceptions import UserError, ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning
import requests
import time
import json
from odoo.http import request
from odoo import http
from odoo import exceptions

_logger = logging.getLogger(__name__)


class electronic_invoice_fields(models.Model):
    _inherit = "account.move"
    is_company_config = fields.Boolean('Has FE', compute='compute_active_fe')
    lastFiscalNumber = fields.Char(
        string="Número Fiscal", compute="on_change_state", readonly="True", store="False")
    puntoFactFiscal = fields.Char(
        string="Punto Facturación Fiscal", readonly="True",
        default=''
    )
    pagadoCompleto = fields.Char(
        string="Estado de Pago", compute="on_change_pago", readonly="True", store="False")
    qr_code = fields.Binary("QR Factura Electrónica",
                            attachment=True, readonly="True", copy=False)
    tipo_documento_fe = fields.Selection(
        string='Tipo de Documento',
        readonly="True",
        selection=[
            ('01', 'Factura de operación interna'),
            ('02', 'Factura de importación'),
            ('03', 'Factura de exportación'),
            ('04', 'Nota de Crédito referente a una FE'),
            ('05', 'Nota de Débito referente a una FE'),
            ('06', 'Nota de Crédito genérica'),
            ('07', 'Nota de Débito genérica'),
            ('08', 'Factura de Zona Franca'),
            ('09', 'Reembolso'),
        ],
        default='01',
        help='Tipo de Documento para Factura Eletrónica.'
    )
    tipo_emision_fe = fields.Selection(
        string='Tipo de Emisión',
        readonly="True",
        selection=[
            ('01', 'Autorización de Uso Previa, operación normal'),
            ('02', 'Autorización de Uso Previa, operación en contingencia'),
            ('03', 'Autorización de Uso Posterior, operación normal'),
            ('04', ' Autorización de Uso posterior, operación en contingencia')
        ],
        default='01',
        help='Tipo de Emisión para Factura Eletrónica.'
    )
    fecha_inicio_contingencia = fields.Date(
        string='Fecha Inicio de Contingencia')
    motivo_contingencia = fields.Char(string='Motivo de Contingencia')
    naturaleza_operacion_fe = fields.Selection(
        string='Naturaleza de Operación',
        selection=[
            ('01', 'Venta'),
            ('02', 'Exportación'),
            ('10', 'Transferencia'),
            ('11', 'Devolución'),
            ('12', 'Consignación'),
            ('13', 'Remesa'),
            ('14', 'Entrega gratuita'),
            ('20', 'Compra'),
            ('21', 'Importación'),
        ],
        default='01',
        help='Naturaleza de Operación para Factura Eletrónica.'
    )
    tipo_operacion_fe = fields.Selection(
        string='Tipo de Operación',
        selection=[
            ('1', 'Salida o venta'),
            ('2', 'Entrada o compra (factura de compra- para comercio informal. Ej.: taxista, trabajadores manuales)'),
        ],
        default='1',
        help='Tipo de Operación para Factura Eletrónica.'
    )
    destino_operacion_fe = fields.Selection(
        string='Destino de Operación',
        selection=[
            ('1', 'Panamá'),
            ('2', 'Extranjero'),
        ],
        default='1',
        help='Destino de Operación para Factura Eletrónica.'
    )
    formatoCAFE_fe = fields.Selection(
        string='Formato CAFE',
        selection=[
            ('1', 'Sin generación de CAFE: El emisor podrá decidir generar CAFE en cualquier momento posterior a la autorización de uso de FE'),
            ('2', 'Cinta de papel'),
            ('3', 'Papel formato carta.'),
        ],
        default='1',
        help='Formato CAFE Factura Eletrónica.'
    )
    entregaCAFE_fe = fields.Selection(
        string='Entrega CAFE',
        selection=[
            ('1', 'Sin generación de CAFE: El emisor podrá decidir generar CAFE en cualquier momento posterior a la autorización de uso de FE'),
            ('2', 'CAFE entregado para el receptor en papel'),
            ('3', 'CAFE enviado para el receptor en formato electrónico'),
        ],
        default='3',
        help='Entrega CAFE Factura Eletrónica.'
    )
    envioContenedor_fe = fields.Selection(
        string='Envío de Contenedor',
        selection=[
            ('1', 'Normal'),
            ('2', ' El receptor exceptúa al emisor de la obligatoriedad de envío del contenedor. El emisor podrá decidir entregar el contenedor, por cualquier razón, en momento posterior a la autorización de uso, pero no era esta su intención en el momento de la emisión de la FE.'),
        ],
        default='1',
        help='Envío de Contenedor Eletrónica.'
    )
    procesoGeneracion_fe = fields.Selection(
        string='Proceso de Generación',
        selection=[
            ('1', 'Generación por el sistema de facturación del contribuyente (desarrollo propio o producto adquirido)'),
        ],
        default='1',
        readonly=True,
        help='Proceso de Generación de Factura Eletrónica.'
    )
    tipoVenta_fe = fields.Selection(
        string='Tipo de Venta',
        selection=[
            ('1', 'Venta de Giro del negocio'),
            ('2', 'Venta Activo Fijo'),
            ('3', 'Venta de Bienes Raíces'),
            ('4', 'Prestación de Servicio. Si no es venta, no informar este campo'),
        ],
        default='1',
        help='Tipo de venta Factura Eletrónica.'
    )
    tipoSucursal_fe = fields.Selection(
        string='Tipo de Sucursal',
        selection=[
            ('1', 'Mayor cantidad de Operaciones venta al detal (retail)'),
            ('2', 'Mayor cantidad de Operaciones venta al por mayor')
        ],
        default='1',
        help='Tipo de sucursal Eletrónica.'
    )

    reversal_reason_fe = fields.Char(
        string='Reason', readonly="True", store="False")
    anulado = fields.Char(string='Anulado', readonly="True", store="False")
    nota_credito = fields.Char(
        string='Nota de Crédito', readonly="True", compute="on_change_type")
    total_precio_descuento = fields.Float(
        string="Precio Descuento",
        default=0.00,
        store="False"
    )
    hsfeURLstr = fields.Char(
        string='HermecURL', readonly="True", store="False")
    pdfNumber = fields.Char(string="PDF Fiscal Number",
                            store="False", copy=False)
    tipoDocPdf = fields.Char(
        string="PDF Tipo Documento", store="False", copy=False)
    tipoEmisionPdf = fields.Char(
        string="PDF Tipo Emisión", store="False", copy=False)
    api_token = fields.Char(string="ApiToken")
    puntoFacturacion = fields.Char(
        string="Punto Fac", store="False",
        default=''
    )
    cafe = fields.Char(string='CAFE', readonly="True", store="False")
    qr_pos = fields.Char(string='QR POS', readonly="True", store="False")
    status_FE = fields.Char(string='Factura Electrónica',
                            readonly="True", store="True",
                            default='Borrador'
                            )

    @ api.depends('qr_code')
    def on_change_pago(self):
        for record in self:
            if str(record.qr_code) != "False":
                record.pagadoCompleto = 'FECompletada'
            else:
                record.pagadoCompleto = 'Pendiente'

    @ api.depends('state')
    def on_change_state(self):

        # return {}

        for record in self:
            config_document_obj = self.env["electronic.invoice"].search(
                [('fe_company_config', '=', record.company_id.id)], limit=1)
            if not config_document_obj.name:
                record.pagadoCompleto = "Finalizado"
            if record.state == 'posted' and record.pagadoCompleto != "NumeroAsignado":
                #record.pagadoCompleto = "NumeroAsignado"
                if record.lastFiscalNumber == False or record.lastFiscalNumber == "0000000000" and (record.move_type == "out_invoice" or record.move_type == "out_refund"):

                    document = self.get_fe_config(
                        record.company_id, record.move_type, True)
                    if document:
                        record.hsfeURLstr = document.hsfeURL
                        record.status_FE = "Pendiente"
                        record.pagadoCompleto = ""

                        # if record.move_type == 'out_refund':
                        #     record.lastFiscalNumber = (
                        #         str(document.numeroDocumentoFiscalNC).rjust(10, '0'))
                        #     document.numeroDocumentoFiscalNC = str(
                        #         int(document.numeroDocumentoFiscalNC) + 1)
                        # else:
                        #     record.lastFiscalNumber = (
                        #         str(document.numeroDocumentoFiscal).rjust(10, '0'))
                        #     document.numeroDocumentoFiscal = str(
                        #         int(document.numeroDocumentoFiscal) + 1)

                        record.puntoFactFiscal = (
                            str(document.puntoFacturacionFiscal).rjust(3, '0'))

    @ api.depends('move_type', 'partner_id')
    def on_change_type(self):
        if self.move_type:
            for record in self:
                if record.move_type == 'out_refund' and str(record.amount_residual) == "0.0":
                    record.tipo_documento_fe = "04"
                    record.nota_credito = "NotaCredito"
                else:
                    record.nota_credito = ""
                    if record.move_type == 'out_refund' and record.state == "draft" and record.reversed_entry_id.id != False:
                        original_invoice_id = self.env["account.move"].search(
                            [('id', '=', self.reversed_entry_id.id)], limit=1)
                        if original_invoice_id:
                            logging.info("Pagado")
                            self.tipo_documento_fe = "04"
                            self.nota_credito = "NotaCredito"
                            # payment = original_invoice_id.amount_residual
                            # inv_monto_total = original_invoice_id.amount_total
                            # if payment != inv_monto_total:
                            # record.tipo_documento_fe = "09"
                            # record.nota_credito = "Reembolso"
                            # else:
                            # self.tipo_documento_fe = "04"
                            # self.nota_credito = "NotaCredito"
                    else:
                        if record.move_type == 'out_refund' and record.state == "draft" and record.reversed_entry_id.id == False:
                            record.tipo_documento_fe = "06"
                            record.nota_credito = "NotaCredito"
        else:
            record.nota_credito = ""

    # HSFE HSServices Calls Security.

    def get_connection(self):
        files = []
        headers = {}
        user = ""
        hsurl = ""
        password = ""
        # constultamos el objeto de nuestra configuración del servicio
        config_document_obj = self.get_fe_config(self.company_id)
        if config_document_obj:
            user = config_document_obj.hsUser
            password = config_document_obj.hsPassword
            hsurl = config_document_obj.hsfeURL

        url = hsurl + "api/token"
        payload = {'username': user,
                   'password': password,
                   'client_id': self.get_ss_info()}

        response = requests.request(
            "POST", url, headers=headers, data=payload, files=files)
        respuesta = json.loads(response.text)
        logging.info("RES" + str(respuesta))

        if("access_token" in respuesta):
            self.api_token = respuesta["access_token"]
            self.send_fiscal_doc()
        else:
            self.status_FE = "Error"
            body = "HS Services <br> <b style='color:red;'>Error -- " + \
                ":</b> (" + str(respuesta['detail']) + ")<br>"
            self.message_post(body=body)
            logging.info("ERROR: Connection Fail -- "
                         + str(respuesta["detail"]))

    def get_connection_reembolso(self):
        self.tipo_documento_fe = "09"
        self.nota_credito = "Reembolso"
        files = []
        headers = {}
        user = ""
        hsurl = ""
        password = ""
        # constultamos el objeto de nuestra configuración del servicio
        config_document_obj = self.get_fe_config(self.company_id)
        if config_document_obj:
            user = config_document_obj.hsUser
            password = config_document_obj.hsPassword
            hsurl = config_document_obj.hsfeURL

        url = hsurl + "api/token"
        payload = {'username': user,
                   'password': password,
                   'client_id': self.get_ss_info()}

        response = requests.request(
            "POST", url, headers=headers, data=payload, files=files)
        respuesta = json.loads(response.text)
        logging.info("RES" + str(respuesta))

        if("access_token" in respuesta):
            self.api_token = respuesta["access_token"]
            self.send_fiscal_doc()
        else:
            self.status_FE = "Error"
            body = "HS Services <br> <b style='color:red;'>Error -- " + \
                ":</b> (" + str(respuesta['detail']) + ")<br>"
            self.message_post(body=body)
            logging.info("ERROR: Connection Fail -- "
                         + str(respuesta["detail"]))

    def get_pdf_token(self):
        files = []
        headers = {}
        user = ""
        hsurl = ""
        password = ""
        # constultamos el objeto de nuestra configuración del servicio
        config_document_obj = self.get_fe_config(self.company_id)
        if config_document_obj:
            user = config_document_obj.hsUser
            password = config_document_obj.hsPassword
            hsurl = config_document_obj.hsfeURL

        url = hsurl + "api/token"
        payload = {'username': user,
                   'password': password,
                   'client_id': self.get_ss_info()}

        response = requests.request(
            "POST", url, headers=headers, data=payload, files=files)
        respuesta = json.loads(response.text)
        logging.info("RES" + str(respuesta))

        if("access_token" in respuesta):
            self.api_token = respuesta["access_token"]
            self.get_pdf_fe()
        else:
            self.status_FE = "Error"
            body = "HS Services <br> <b style='color:red;'>Error -- " + \
                ":</b> (" + str(respuesta['detail']) + ")<br>"
            self.message_post(body=body)
            logging.info("ERROR: Connection Fail -- "
                         + str(respuesta["detail"]))

    def get_recall_token(self):
        files = []
        headers = {}
        user = ""
        hsurl = ""
        password = ""
        # constultamos el objeto de nuestra configuración del servicio
        config_document_obj = self.get_fe_config(self.company_id)
        if config_document_obj:
            user = config_document_obj.hsUser
            password = config_document_obj.hsPassword
            hsurl = config_document_obj.hsfeURL

        url = hsurl + "api/token"
        payload = {'username': user,
                   'password': password,
                   'client_id': self.get_ss_info()}

        response = requests.request(
            "POST", url, headers=headers, data=payload, files=files)
        respuesta = json.loads(response.text)
        logging.info("RES" + str(respuesta))

        if("access_token" in respuesta):
            self.api_token = respuesta["access_token"]
            self.get_all_info_fe()
        else:
            self.status_FE = "Error"
            body = "HS Services <br> <b style='color:red;'>Error -- " + \
                ":</b> (" + str(respuesta['detail']) + ")<br>"
            self.message_post(body=body)
            logging.info("ERROR: Connection Fail -- "
                         + str(respuesta["detail"]))

    def send_fiscal_doc(self):
        original_invoice_values = {}
        retencion = {}
        nlastFiscalNumber = ""
        original_invoice_id = self.env["account.move"].search(
            [('id', '=', self.reversed_entry_id.id)], limit=1)

        if original_invoice_id:
            last_invoice_number = original_invoice_id.name
            original_invoice_info = self.env["electronic.invoice.moves"].search(
                [('invoiceNumber', '=', last_invoice_number)], limit=1)
            if original_invoice_info:
                nlastFiscalNumber = original_invoice_info.numeroDocumentoFiscal

            original_invoice_values = {
                "lastFiscalNumber": nlastFiscalNumber,
                "tipoDocumento": "01",
                "tipoEmision": "01"
            }

        # constultamos el objeto de nuestra configuración del servicio
        config_document_obj = self.get_fe_config(self.company_id)
        if config_document_obj:
            tokenEmpresa = config_document_obj.tokenEmpresa
            tokenPassword = config_document_obj.tokenPassword
            codigoSucursal = config_document_obj.codigoSucursalEmisor
            url_wsdl = config_document_obj.wsdl
            self.puntoFacturacion = config_document_obj.puntoFacturacionFiscal
            varhsfeURLstr = config_document_obj.hsfeURL
            self.hsfeURLstr = config_document_obj.hsfeURL

        url = varhsfeURLstr + "api/send"

        precioDescuento = '0'
        for item in self.invoice_line_ids:
            if item.discount > 0:
                precioDescuento = str(
                    (float(item.price_unit) * float(item.discount)) / 100)
                self.total_precio_descuento += float(precioDescuento)

        if(len(self.amount_by_group) > 1):
            retencion = {
                'codigoRetencion': "2",
                'montoRetencion': str('%.2f' % round((self.amount_total - self.amount_untaxed), 2))
            }

        all_values = json.dumps({
            "wsdl_url": url_wsdl,
            "tokenEmpresa": tokenEmpresa,
            "tokenPassword": tokenPassword,
            "codigoSucursalEmisor": codigoSucursal,
            "tipoSucursal": self.tipoSucursal_fe if self.tipoSucursal_fe else '1',
            "datosTransacion": self.get_transaction_data(),
            "listaItems": self.get_items_invoice_info(),
            "subTotales": self.get_sub_totals(),
            "listaFormaPago": self.get_array_payment_info(),
            "amount_residual": self.amount_residual,
            "original_invoice": original_invoice_values,
            "retencion": retencion,
            "descuentoBonificacion": {
                "descDescuento": "Descuentos aplicados a los productos",
                # str('%.2f' % round(self.total_precio_descuento, 2))
                "montoDescuento": "0.00"
            }
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + str(self.api_token)
        }

        logging.info("VALUES SEND" + str(all_values))

        if(self.partner_id.email):
            if(self.partner_id.TipoClienteFE):

                try:
                    res = requests.request(
                        "POST", url, headers=headers, data=all_values)
                    logging.info("RES::::::::" + str(res))
                    respuesta = json.loads(res.text)
                    logging.info("RES" + str(respuesta))

                    if(int(respuesta["codigo"]) == 200):
                        self.status_FE = "Factura Creada"
                        # ESTA OPCION ES PARA MOSTRAR MENSAJE LUEGO DEL CREATE
                        self.insert_data_to_electronic_invoice_moves(
                            respuesta, self.name)
                        self.pdfNumber = respuesta["numeroDocumentoFiscal"]
                        self.tipoDocPdf = respuesta["tipoDocumento"]
                        self.tipoEmisionPdf = respuesta["tipoEmision"]

                        tipo_doc_text = respuesta['mensaje']

                        if 'qr' in respuesta and 'cufe' in respuesta:
                            self.qr_pos = str(respuesta['qr'])
                            self.cafe = str(respuesta['cufe'])
                            tipo_doc_text = "Factura Electrónica Creada" + \
                                " :<br> <b>CUFE:</b> (<a target='_blank' href='" + \
                                respuesta['qr'] + "'>" + \
                                str(respuesta['cufe']) + ")</a><br>"
                            if self.tipo_documento_fe == "04":
                                tipo_doc_text = "Nota de Crédito Creada" + \
                                    " :<br> <b>CUFE:</b> (<a target='_blank' href='" + \
                                    respuesta['qr'] + "'>" + \
                                    str(respuesta['cufe']) + ")</a><br>"

                        if self.tipo_documento_fe == "09":
                            tipo_doc_text = "Reembolso Creado Correctamente."

                        body = tipo_doc_text

                        self.message_post(body=body)

                        # add QR in invoice info
                        if 'qr' in respuesta:
                            self.generate_qr(respuesta)

                        # self.download_pdf(self.lastFiscalNumber, respuesta['pdf_document'])
                        if respuesta['mensaje'] == "Proceso de Anulación ejecutado con éxito.":
                            # original_invoice_id.state = "cancel"
                            original_invoice_id.status_FE = "Anulado"
                        self.pagadoCompleto = "FECompletada"
                        """  return {
                               'name': _('Successfull'),
                               'type': 'ir.actions.act_window',
                               'view_mode': 'form',
                               'res_model': 'message.wizard',
                               'target': 'new'

                           } """
                    else:
                        if(respuesta['codigo'] != "102"):
                            self.status_FE = "Error"
                            self.insert_data_to_logs(respuesta, self.name)
                            body = "Factura Electrónica No Generada:<br> <b style='color:red;'>Error " + \
                                respuesta['codigo'] + \
                                ":</b> (" + respuesta['mensaje'] + ")<br>"
                            self.message_post(body=body)
                        else:
                            self.status_FE = "Factura Creada"
                            self.pagadoCompleto = "FECompletada"
                            body = "Factura Electrónica Generada Anteriormente, Favor Actualizar la Página. "
                            self.message_post(body=body)

                except NameError:
                    # self.status_FE = "Error"
                    body = str(json.dumps(NameError))
                    # body = "Factura Electrónica No Generada:<br> <b style='color:red;'>Error:</b> (El tipo de cliente de factura electrónica, no ha sido especificado, por favor asegurese de ingresar este valor.)<br>"
                    # self.message_post(body=body)

            else:
                #mymodule = self.get_server_info(self.name)
                # logging.info("MSG ID:::::::::" + str(message_id))
                body = "Factura Electrónica No Generada:<br> <b style='color:red;'>Error:</b> (El tipo de cliente de factura electrónica, no ha sido especificado, por favor asegurese de ingresar este valor.)<br>"
                self.set_msg_error(body)
                # time.sleep(2)

                # raise ValidationError("This is error message.")
                # action = self.env.ref('account.action_account_config')
                # msg = _(
                # 'Cannot find a chart of accounts for this company.\nPlease go to Account Configuration.')
                # raise RedirectWarning(msg, action.id, _(
                # 'Aceptar'))

                # return {'warning': {
                # 'title': "Warning",
                # 'message': "There is no joining date defined for this employee",
                # }
                # }
                # raise except_orm('Warning', 'Factura Electrónica No Generada:')
                # if self.status_FE == "Error":
                # raise UserError(
                # _("Factura Electrónica No Generada:(El tipo de cliente de factura electrónica, no ha sido especificado, por favor asegurese de ingresar este valor.)"))
        else:
            self.status_FE = "Error"
            body = "Factura Electrónica No Generada:<br> <b style='color:red;'>Error:</b> (El cliente no posee un correo electrónico, por favor asegurese de ingresar este valor.)<br>"

            message_id = self.message_post(body=body)
            if self.status_FE == "Error":
                raise UserError(
                    _("Factura Electrónica No Generada:>Error: (El cliente no posee un correo electrónico, por favor asegurese de ingresar este valor.)"))

    def get_array_payment_info(self):
        url = self.hsfeURLstr + "api/listpayments"
        payment_value_str = "99"
        payments_real = []
        payments_completes = []
        payments_real_desc = []

        if self.invoice_payments_widget != 'false':
            raw_data = self.invoice_payments_widget
            payment = json.loads(raw_data)
            refunds = payment["content"]

            payment_method = {
                "Tarjeta de Crédito": "03",
                "Tarjeta Clave": "04",
                "ACH": "08",
                "Efectivo": "02",
                "Electrónico": "99",
                "Deposito en Efectivo": "08",
                "Cheque": "09",
                "Banco": "99",
                "Manual": "99"
            }

            for content in refunds:
                refund_id = content["move_id"]
                if 'pos_payment_name' in content:
                    payment_name = content["pos_payment_name"]
                journal_name = content["journal_name"]
                temp = self.env["account.move"].search(
                    [('id', '=', refund_id)])

                #logging.info("WIDGET:::::::::  " + temp.move_type)
                if temp.move_type in ['out_invoice', 'out_refund'] or journal_name == 'Point of Sale':
                    if journal_name == 'Point of Sale':
                        payments_real.append(temp.amount_total)
                        payment_value_str = payment_method[payment_name]
                        payments_real_desc.append({"code": payment_value_str,
                                                   "desc": temp.name
                                                   })
                    else:
                        payments_real.append(temp.amount_total)
                        payment_value_str = "99"
                        payments_real_desc.append({"code": payment_value_str,
                                                   "desc": temp.name
                                                   })
                else:
                    payments_completes = self.env["account.payment"].search(
                        [('move_id', '=', temp.id)])
                    for item in payments_completes:
                        payments_real.append(item.amount)
                        # payments_real_desc.append(temp.journal_id.name)
                        payment_value_str = payment_method[item.payment_method_id.name]
                        logging.info("Entró IF de metodo pago")
                        payments_real_desc.append({"code": payment_value_str,
                                                   "desc": item.payment_method_id.name
                                                   })

            logging.info(
                "PAGOS CODIGO WIDGET PAYMENT:::::::::::::::::::" + str(payments_real))
            logging.info(
                "DESC CODIGO WIDGET PAYMENT:::::::::::::::::::" + str(payments_real_desc))
        else:
            payment_value_str = "01"
            payments_real_desc.append({"code": payment_value_str,
                                       "desc": "Crédito"
                                       })

        payments = payments_real

        payment_values = json.dumps({
            "payments_items": payments,
            "monto_impuesto_completo": self.amount_by_group[0][1] if len(self.amount_by_group) > 1 else self.amount_by_group[0][1] if len(self.amount_by_group) == 1 else 0.00,
            "amount_untaxed": self.amount_untaxed,
            "amount_retention_tax": abs(self.amount_by_group[1][1]) if len(self.amount_by_group) > 1 else 0.00,
            "payment_method": payments_real_desc,
            "total_discount_price": 0.00  # self.total_precio_descuento
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + str(self.api_token)
        }

        logging.info("PAYMENTS VALUES::::::::" + str(payment_values))
        response = requests.request(
            "POST", url, headers=headers, data=payment_values)
        logging.info('Info AZURE PAGOS: ' + str(response.text))
        return json.loads(response.text)

    def get_transaction_data(self):
        url = self.hsfeURLstr + "api/transactiondata"
        cufe_fe_cn = ""
        last_invoice_number = ""
        date_referenciado_str = ""

        original_invoice_id = self.env["account.move"].search(
            [('id', '=', self.reversed_entry_id.id)], limit=1)
        if original_invoice_id:
            last_invoice_number = original_invoice_id.name

        original_invoice_info = self.env["electronic.invoice.moves"].search(
            [('invoiceNumber', '=', last_invoice_number)], limit=1)
        if original_invoice_info:
            cufe_fe_cn = original_invoice_info.cufe
            date_referenciado_str = original_invoice_info.fechaRDGI

        fiscalReferenciados = {
            # .strftime("%Y-%m-%dT%H:%M:%S-05:00"),.....
            "fechaEmisionDocFiscalReferenciado": date_referenciado_str,
            "cufeFEReferenciada": cufe_fe_cn,
        }

        transaction_values = json.dumps({
            "tipoEmision": self.tipo_emision_fe if self.tipo_emision_fe else '01',
            "tipoDocumento": self.tipo_documento_fe,
            "numeroDocumentoFiscal": self.lastFiscalNumber,
            "puntoFacturacionFiscal": self.puntoFacturacion,
            "naturalezaOperacion": self.naturaleza_operacion_fe if self.naturaleza_operacion_fe else '01',
            "tipoOperacion": self.tipo_operacion_fe if self.tipo_operacion_fe else '1',
            "destinoOperacion": self.destino_operacion_fe if self.destino_operacion_fe else '1',
            "formatoCAFE": self.formatoCAFE_fe if self.formatoCAFE_fe else '1',
            "entregaCAFE": self.entregaCAFE_fe if self.entregaCAFE_fe else '3',
            "envioContenedor": self.envioContenedor_fe if self.envioContenedor_fe else '1',
            "procesoGeneracion": self.procesoGeneracion_fe if self.procesoGeneracion_fe else '1',
            "tipoVenta": self.tipoVenta_fe if self.tipoVenta_fe else '1',
            "informacionInteres": self.narration if self.narration else "",
            "fechaEmision": self.invoice_date.strftime("%Y-%m-%dT%H:%M:%S-05:00"),
            "cliente": self.get_client_info(),
            "fechaInicioContingencia": self.fecha_inicio_contingencia.strftime("%Y-%m-%dT%I:%M:%S-05:00") if self.fecha_inicio_contingencia else None,
            "motivoContingencia": "Motivo Contingencia: " + str(self.motivo_contingencia) if self.motivo_contingencia else "Motivo Contingencia: N/A",
            "listaDocsFiscalReferenciados": fiscalReferenciados
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + str(self.api_token)
        }
        logging.info("Transactions Values HS HERMEC" + str(transaction_values))
        response = requests.request(
            "POST", url, headers=headers, data=transaction_values)
        logging.info('Info AZURE TRANSACTION DATA: ' + str(response.text))
        return json.loads(response.text)

    def get_client_info(self):
        url = self.hsfeURLstr + "api/client"
        logging.info("CLIENTE::::::" + str(self.partner_id.name))
        client_values = json.dumps({
            "tipoClienteFE": self.partner_id.TipoClienteFE,
            "tipoContribuyente": self.partner_id.tipoContribuyente if self.partner_id.tipoContribuyente is not False else "2",
            "numeroRUC": self.partner_id.numeroRUC,
            "pais": self.partner_id.country_id.code if self.destino_operacion_fe == "Extranjero" else "PA",
            "correoElectronico1": self.partner_id.email,
            "telefono1": str(self.partner_id.phone).replace("+507 ", "") if self.partner_id.phone is not False else "",
            "digitoVerificadorRUC": self.partner_id.digitoVerificadorRUC,
            "razonSocial": self.partner_id.name,
            "direccion": self.partner_id.street + "/" + self.partner_id.street2 if self.partner_id.street is not False and self.partner_id.street2 is not False else self.partner_id.street if self.partner_id.street is not False else "",
            "codigoUbicacion": self.partner_id.CodigoUbicacion,
            "provincia": self.partner_id.provincia,
            "distrito": self.partner_id.distrito,
            "corregimiento": self.partner_id.corregimiento,
            "tipoIdentificacion": self.partner_id.tipoIdentificacion,
            "nroIdentificacionExtranjero": self.partner_id.nroIdentificacionExtranjero,
            "paisExtranjero": self.partner_id.country_id.name,
        })
        # , ensure_ascii=False
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer ' + str(self.api_token)
        }

        logging.info("Cliente Enviado:" + str(client_values))
        response = requests.request(
            "POST", url, headers=headers, data=client_values)
        # logging.info("URL Odoo:" + str(request.httprequest.host_url))

        logging.info('Info AZURE CLIENTE: ' + str(response.text))
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            self.status_FE = "Error"

    def get_sub_totals(self):
        url = self.hsfeURLstr + "api/subtotals"
        # payments_items_by_recid = self.env['account.payment'].search(
        # []).filtered(lambda p: self.id in p.reconciled_invoice_ids.ids)
        payments_real = []
        # payments2 = [item.amount for item in payments_items]
        # payments = [item.amount for item in payments_items_by_recid]

        if self.invoice_payments_widget != 'false':
            raw_data = self.invoice_payments_widget
            payment = json.loads(raw_data)
            refunds = payment["content"]

            for content in refunds:
                refund_id = content["move_id"]
                temp = self.env["account.move"].search(
                    [('id', '=', refund_id)])

                if temp.move_type in ['out_invoice', 'out_refund']:
                    payments_real.append(temp.amount_total)
                else:
                    payments_completes = self.env["account.payment"].search(
                        [('move_id', '=', temp.id)])
                    for item in payments_completes:
                        payments_real.append(item.amount)
            logging.info(
                "PAGOS CODIGO WIDGET PAYMENT:::::::::::::::::::" + str(payments_real))

        payments = payments_real

        # logging.info("Valores de Payments By Reference: " + str(payments))
        # logging.info("Valores de Payments By Reconcile ID: " + str(payments2))

        # logging.info("Valores de Payments Widget: " +
        #              str(self.invoice_payments_widget))
        # logging.info(str(self.amount_by_group[0][2]))
        # logging.info("Valores de ITBMS: 1" + str(self.amount_by_group[1][0]))
        # logging.info(str(self.amount_by_group[1][1]))

        sub_total_values = json.dumps({
            "amount_untaxed": self.amount_untaxed,
            "amount_tax_completed": self.amount_by_group[0][1] if len(self.amount_by_group) > 1 else self.amount_by_group[0][1] if len(self.amount_by_group) == 1 else 0.00,
            # abs(self.amount_by_group[1][1]) if len(self.amount_by_group) > 1 else 0.00,
            "amount_retention_tax": abs(self.amount_by_group[1][1]) if len(self.amount_by_group) > 1 else 0.00,
            "total_discount_price": 0.00,  # self.total_precio_descuento,
            "items_qty": str(len(self.invoice_line_ids)),
            "payment_time": 1,
            "array_total_items_value": payments,
            "array_payment_form": self.get_array_payment_info()
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + str(self.api_token)
        }
        logging.info("SUBTOTALES Values HS HERMEC" + str(sub_total_values))
        response = requests.request(
            "POST", url, headers=headers, data=sub_total_values)
        # logging.info('Info AZURE SUBTOTALES: ' + str(response.text))
        return json.loads(response.text)

    def generate_qr(self, res):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(res['qr'])
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image

    def download_pdf(self, fiscalNumber, document):
        b64 = str(document)
        b64_pdf = b64  # base64.b64encode(pdf[0])
        # save pdf as attachment
        name = fiscalNumber
        return self.env['ir.attachment'].create({
            'name': name + str(".pdf"),
            'type': 'binary',
            'datas': b64_pdf,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })

    def insert_data_to_electronic_invoice_moves(self, res, invoice_number):

        # Save the move info
        self.env['electronic.invoice.moves'].create({
            'cufe': res['cufe'] if 'cufe' in res else "",
            'qr': res['qr'] if 'qr' in res else "",
            'invoiceNumber': invoice_number,
            # res['fechaRecepcionDGI'] if 'fechaRecepcionDGI' in res else "",
            'fechaRDGI': self.invoice_date.strftime("%Y-%m-%dT%H:%M:%S-05:00"),
            'numeroDocumentoFiscal': self.lastFiscalNumber,
            'puntoFacturacionFiscal': self.puntoFactFiscal,
        })

    def insert_data_to_logs(self, res, invoice_number):

        self.env['electronic.invoice.logs'].create({
            'codigo': res['codigo'],
            'mensaje': res['mensaje'],
            'resultado': res['resultado'],
            'invoiceNumber': invoice_number
        })

    def get_items_invoice_info(self):
        url = self.hsfeURLstr + "api/items"
        itemLoad = []
        array_tax_item = []
        contador = 0
        sonumber =''
        origin_so = self.env["sale.order"].search(
            [('invoice_ids', '=', self.id)], limit=1)
        if origin_so:
            sonumber = origin_so.name
          
        #invoice_ids
        if self.invoice_line_ids:
            for item in self.invoice_line_ids:
                array_tax_item = []
                if item.tax_ids:
                    for tax_item in item.tax_ids:
                        # rray_tax_item = []
                        logging.info("VALOR DE ITMBS "
                                     + str(tax_item.amount) + " Amount TYPE::" + str(tax_item.amount_type))
                        if tax_item.amount_type == 'percent' and tax_item.amount > 0:

                            array_tax_item.append({
                                'amount_type': tax_item.amount_type,
                                'amount': tax_item.amount
                            })
                        elif tax_item.amount_type == 'group':
                            array_children = []

                            for child_tax_item in tax_item.children_tax_ids:

                                array_children.append(
                                    {
                                        'child_name': str(child_tax_item.name),
                                        'child_amount': str(child_tax_item.amount)
                                    })
                            array_tax_item.append({
                                'amount_type': tax_item.amount_type,
                                'amount': tax_item.amount,
                                'group_tax_children': array_children
                            })
                else:
                    array_tax_item.append({
                        'amount_type': 'percent',
                        'amount': '0'
                    })

                logging.info("array_tax_item:::::::::::::"
                             + str(array_tax_item))

                descripcion = str(item.product_id.name)
                if contador == 0 and sonumber != '':
                    descripcion = 'Pedido de Venta: ['+sonumber+'] ' + descripcion
                
                itemLoad.append({
                    'typeCustomers': str(self.partner_id.TipoClienteFE),
                    'categoriaProducto': str(item.product_id.categoryProduct) if item.product_id.categoryProduct else "",
                    'descripcion': descripcion, #str(item.product_id.name),
                    'codigo': str(item.product_id.default_code) if item.product_id.default_code else "",
                    'arrayTaxes': array_tax_item,
                    'cantidad': item.quantity,
                    'precioUnitario': item.price_unit,
                    'precioUnitarioDescuento': item.discount,
                    'codigoGTIN': str(item.product_id.codigoGTIN) if item.product_id.codigoGTIN else "",
                    'cantGTINCom': item.product_id.cantGTINCom if item.product_id.cantGTINCom else "",
                    'codigoGTINInv': item.product_id.codigoGTINInv if item.product_id.cantGTINCom else "",
                    'cantGTINComInv': item.product_id.cantGTINComInv if item.product_id.cantGTINComInv else "",
                    'fechaFabricacion': str(item.product_id.fechaFabricacion).strftime("%Y-%m-%dT%H:%M:%S-05:00") if item.product_id.fechaFabricacion else datetime.today().strftime("%Y-%m-%dT%H:%M:%S-05:00"),
                    'fechaCaducidad': str(item.product_id.fechaCaducidad).strftime("%Y-%m-%dT%H:%M:%S-05:00") if item.product_id.fechaCaducidad else datetime.today().strftime("%Y-%m-%dT%H:%M:%S-05:00"),
                    'codigoCPBS': str(item.product_id.codigoCPBS),
                    'unidadMedidaCPBS': str(item.product_id.unidadMedidaCPBS),
                    'codigoCPBSAbrev': str(item.product_id.codigoCPBSAbrev),
                    'tasaISC': str(item.product_id.tasaISC),
                    'precioAcarreo': item.product_id.precioAcarreo if item.product_id.precioAcarreo else 0.00,
                    'precioSeguro': item.product_id.precioSeguro if item.product_id.precioSeguro else 0.00,
                    'infoItem': str(item.product_id.infoItem) if item.product_id.infoItem else "",
                    'tasaOTI': str(item.product_id.tasaOTI) if item.product_id.tasaOTI else "",
                    'valorTasa': item.product_id.valorTasa if item.product_id.valorTasa else 0.00,
                })
                contador += 1
                # self.narration if self.narration else "",
            logging.info("ITEMS ENVIADOS::::::" + str(itemLoad))
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + str(self.api_token)
        }
        dataJsonItem = {"list_items": itemLoad}
        response = requests.request(
            "POST", url, headers=headers, data=json.dumps(dataJsonItem))
        return json.loads(response.text)

    def get_pdf_fe_pos(self):
        pdf_doc = ""
        self.pagadoCompleto = "Finalizado"
        # constultamos el objeto de nuestra configuración del servicio
        config_document_obj = self.get_fe_config(self.company_id)
        if config_document_obj:
            tokenEmpresa = config_document_obj.tokenEmpresa
            tokenPassword = config_document_obj.tokenPassword
            codigoSucursal = config_document_obj.codigoSucursalEmisor
            url_wsdl = config_document_obj.wsdl
            hs_url = config_document_obj.hsfeURL
            self.puntoFacturacion = config_document_obj.puntoFacturacionFiscal
        url = hs_url + "api/pdf"

        pdf_values = json.dumps({
            "wsdl_url": url_wsdl,
            "codigoSucursalEmisor": codigoSucursal,
            "tokenEmpresa": tokenEmpresa,
            "tokenPassword": tokenPassword,
            "tipoEmision": self.tipoEmisionPdf,
            "tipoDocumento": self.tipoDocPdf,
            "numeroDocumentoFiscal": self.pdfNumber,
            "puntoFacturacionFiscal": self.puntoFacturacion,

        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + str(self.api_token)
        }

        logging.info('Enviado PDF:: ' + str(pdf_values))

        correcto = False
        # logging.info("PD 64" + str(response))
        while correcto != True:
            response = requests.request(
                "POST", url, headers=headers, data=pdf_values)
            respuesta = json.loads(response.text)
            logging.info('Resultado PDF:: ' + str(response.text))
            if respuesta["codigo"] == "200":
                correcto = True
                pdf_doc = str(respuesta["documento"])
                self.download_pdf(self.pdfNumber, str(respuesta["documento"]))

        return pdf_doc

    def get_pdf_fe(self):
        self.pagadoCompleto = "Finalizado"
        # constultamos el objeto de nuestra configuración del servicio
        config_document_obj = self.get_fe_config(self.company_id)
        if config_document_obj:
            tokenEmpresa = config_document_obj.tokenEmpresa
            tokenPassword = config_document_obj.tokenPassword
            codigoSucursal = config_document_obj.codigoSucursalEmisor
            url_wsdl = config_document_obj.wsdl
            self. puntoFacturacion = config_document_obj.puntoFacturacionFiscal
        url = self.hsfeURLstr + "api/pdf"

        pdf_values = json.dumps({
            "wsdl_url": url_wsdl,
            "codigoSucursalEmisor": codigoSucursal,
            "tokenEmpresa": tokenEmpresa,
            "tokenPassword": tokenPassword,
            "tipoEmision": self.tipoEmisionPdf,
            "tipoDocumento": self.tipoDocPdf,
            "numeroDocumentoFiscal": self.pdfNumber,
            "puntoFacturacionFiscal": self.puntoFacturacion,

        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + str(self.api_token)
        }

        logging.info('Enviado PDF:: ' + str(pdf_values))

        correcto = False
        # logging.info("PD 64" + str(response))
        while correcto != True:
            response = requests.request(
                "POST", url, headers=headers, data=pdf_values)
            respuesta = json.loads(response.text)
            logging.info('Resultado PDF:: ' + str(response.text))
            if respuesta["codigo"] == "200":
                correcto = True
                self.download_pdf(self.pdfNumber, str(respuesta["documento"]))

    def get_all_info_fe(self):
        self.pagadoCompleto = "Finalizado"
        # constultamos el objeto de nuestra configuración del servicio
        config_document_obj = self.env["electronic.invoice"].search(
            [('name', '=', 'ebi-pac')], limit=1)
        if config_document_obj:
            tokenEmpresa = config_document_obj.tokenEmpresa
            tokenPassword = config_document_obj.tokenPassword
            codigoSucursal = config_document_obj.codigoSucursalEmisor
            url_wsdl = config_document_obj.wsdl
            self. puntoFacturacion = config_document_obj.puntoFacturacionFiscal
        url = self.hsfeURLstr + "api/documentStatus"

        pdf_values = json.dumps({
            "wsdl_url": url_wsdl,
            "codigoSucursalEmisor": codigoSucursal,
            "tokenEmpresa": tokenEmpresa,
            "tokenPassword": tokenPassword,
            "tipoEmision": self.tipoEmisionPdf,
            "tipoDocumento": self.tipoDocPdf,
            "numeroDocumentoFiscal": self.pdfNumber,
            "puntoFacturacionFiscal": self.puntoFacturacion,

        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + str(self.api_token)
        }

        res = requests.request(
            "POST", url, headers=headers, data=pdf_values)
        respuesta = json.loads(res.text)

        if(int(respuesta["codigo"]) == 200):
            self.status_FE = "Factura Creada"
            # ESTA OPCION ES PARA MOSTRAR MENSAJE LUEGO DEL CREATE
            self.insert_data_to_electronic_invoice_moves(
                respuesta, self.name)
            self.pdfNumber = respuesta["numeroDocumentoFiscal"]
            self.tipoDocPdf = respuesta["tipoDocumento"]
            self.tipoEmisionPdf = respuesta["tipoEmision"]

            tipo_doc_text = respuesta['mensaje']

            if 'qr' in respuesta and 'cufe' in respuesta:
                self.qr_pos = str(respuesta['qr'])
                self.cafe = str(respuesta['cufe'])
                tipo_doc_text = "Factura Electrónica Creada" + \
                    " :<br> <b>CUFE:</b> (<a target='_blank' href='" + \
                    respuesta['qr'] + "'>" + \
                    str(respuesta['cufe']) + ")</a><br>"
                if self.tipo_documento_fe == "04":
                    tipo_doc_text = "Nota de Crédito Creada" + \
                        " :<br> <b>CUFE:</b> (<a target='_blank' href='" + \
                        respuesta['qr'] + "'>" + \
                        str(respuesta['cufe']) + ")</a><br>"

            if self.tipo_documento_fe == "09":
                tipo_doc_text = "Reembolso Creado Correctamente."

            body = tipo_doc_text

            self.message_post(body=body)

            # add QR in invoice info
            if 'qr' in respuesta:
                self.generate_qr(respuesta)
            self.pagadoCompleto = "FECompletada"

    def set_msg_error(self, body):
        logging.info("ENTROOO AL MSG ERROR:::")
        self.status_FE = "Error"
        self.message_post(body=body)

    def get_ss_info(self):
        sscode = ""
        configuracion = self.env["ir.config_parameter"].sudo().search(
            [('key', '=', "database.enterprise_code")])
        if configuracion:
            sscode = configuracion.value

        return sscode

    def get_fe_config(self, company, move_type="out_invoice", isSum=False):

        config_document_obj = self.env["electronic.invoice"].search(
            [('fe_company_config', '=', company.id)], limit=1)

        # company_id = self.env.company.id
        logging.info("ID de la compania " + str(company) +
                     "ISSUCURSAL::::" + str(config_document_obj.is_sucursal))

        # return {}

        if config_document_obj.is_sucursal:
            logging.info("Entro a la sucursal " +
                         str(config_document_obj.fe_principal_company_config))
            logging.info("Datos de la sucursal " + str(config_document_obj))

            principal_conf_obj = self.env["electronic.invoice"].search(
                [('fe_principal_company_config', '=', config_document_obj.fe_principal_company_config.id)], limit=1)

            logging.info("Datos de la company principal " +
                         str(principal_conf_obj))

            if isSum:
                if move_type == 'out_refund':
                    self.lastFiscalNumber = (
                        str(principal_conf_obj.numeroDocumentoFiscalNC).rjust(10, '0'))
                    principal_conf_obj.numeroDocumentoFiscalNC = str(
                        int(principal_conf_obj.numeroDocumentoFiscalNC) + 1)
                else:
                    if move_type == 'out_invoice':
                        self.lastFiscalNumber = (
                            str(principal_conf_obj.numeroDocumentoFiscal).rjust(10, '0'))
                        principal_conf_obj.numeroDocumentoFiscal = str(
                            int(principal_conf_obj.numeroDocumentoFiscal) + 1)

            final_config_obj = Empty()
            final_config_obj.hsUser = principal_conf_obj.hsUser
            final_config_obj.hsPassword = principal_conf_obj.hsPassword
            final_config_obj.hsfeURL = principal_conf_obj.hsfeURL
            final_config_obj.wsdl = principal_conf_obj.wsdl
            final_config_obj.name = principal_conf_obj.name
            final_config_obj.tokenEmpresa = principal_conf_obj.tokenEmpresa
            final_config_obj.tokenPassword = principal_conf_obj.tokenPassword
            final_config_obj.codigoSucursalEmisor = config_document_obj.codigoSucursalEmisor
            final_config_obj.puntoFacturacionFiscal = config_document_obj.puntoFacturacionFiscal

            return final_config_obj

        else:
            logging.info("Entro a la PRINCIPAL ")
            if isSum:
                logging.info("TOCA SUMAR " + str(isSum))
                logging.info("Tipo " + str(move_type))
                logging.info("Numero DOC Fisc " +
                             str(config_document_obj.numeroDocumentoFiscal))
                if move_type == 'out_refund':
                    self.lastFiscalNumber = (
                        str(config_document_obj.numeroDocumentoFiscalNC).rjust(10, '0'))
                    config_document_obj.numeroDocumentoFiscalNC = str(
                        int(config_document_obj.numeroDocumentoFiscalNC) + 1)
                else:
                    if move_type == 'out_invoice':
                        self.lastFiscalNumber = (
                            str(config_document_obj.numeroDocumentoFiscal).rjust(10, '0'))
                        config_document_obj.numeroDocumentoFiscal = str(
                            int(config_document_obj.numeroDocumentoFiscal) + 1)

            final_config_obj = Empty()
            final_config_obj.hsUser = config_document_obj.hsUser
            final_config_obj.hsPassword = config_document_obj.hsPassword
            final_config_obj.hsfeURL = config_document_obj.hsfeURL
            final_config_obj.wsdl = config_document_obj.wsdl
            final_config_obj.name = config_document_obj.name
            final_config_obj.tokenEmpresa = config_document_obj.tokenEmpresa
            final_config_obj.tokenPassword = config_document_obj.tokenPassword
            final_config_obj.codigoSucursalEmisor = config_document_obj.codigoSucursalEmisor
            final_config_obj.puntoFacturacionFiscal = config_document_obj.puntoFacturacionFiscal

            return final_config_obj

    @api.onchange('journal_id')
    @api.depends('journal_id')
    def compute_active_fe(self):
        for invoice in self:
            config_document_obj = self.env["electronic.invoice"].search(
                [('fe_company_config', '=', invoice.company_id.id)], limit=1)
            logging.info("ID de Compañia en compute= " +
                         str(invoice.company_id.id))
            if config_document_obj:
                invoice.is_company_config = True
            else:
                invoice.is_company_config = False

class Empty:
    def __init__(
        self,
        hsUser=None,
        hsPassword=None,
        hsfeURL=None,
        wsdl=None,
        name=None,
        tokenEmpresa=None,
        tokenPassword=None,
        codigoSucursalEmisor=None,
        puntoFacturacionFiscal=None,
    ):
        self.hsUser = hsUser
        self.hsPassword = hsPassword
        self.hsfeURL = hsfeURL
        self.wsdl = wsdl
        self.name = name
        self.tokenEmpresa = tokenEmpresa
        self.tokenPassword = tokenPassword
        self.codigoSucursalEmisor = codigoSucursalEmisor
        self.puntoFacturacionFiscal = puntoFacturacionFiscal
