select detalle.id,
detalle.account_internal_type,
invoice.partner_id,
proveedor.tipo_persona, 
proveedor.vat,
proveedor.partner_dv,
proveedor.name,
invoice.tipo_pago,
detalle.hconcep, detalle.price_subtotal,
invoice.periodo
from account_move_line As detalle , account_move as invoice, res_partner as proveedor
where detalle.move_id = invoice.id and invoice.partner_id = proveedor.id
and invoice.type = 'in_invoice' and detalle.account_internal_type = 'other'
limit 15;




select proveedor.tipo_persona, 
proveedor.vat,
proveedor.partner_dv,
proveedor.name,
invoice.tipo_pago,
detalle.hconcep, 
sum(detalle.price_subtotal),
invoice.periodo
from account_move_line As detalle , account_move as invoice, res_partner as proveedor
where detalle.move_id = invoice.id and invoice.partner_id = proveedor.id
and invoice.type = 'in_invoice' and detalle.account_internal_type = 'other' and invoice.state <> 'draft'
and detalle.exclude_from_invoice_tab = 'f' and detalle.display_type is null and detalle.hconcep > 0
group by proveedor.tipo_persona, proveedor.vat,proveedor.partner_dv,proveedor.name,invoice.tipo_pago,detalle.hconcep,invoice.periodo ;

-- QUERY PARA EL REPORTE DEL ANEXO 94
select proveedor.tipo_persona, 
proveedor.vat,
proveedor.partner_dv,
proveedor.name,
invoice.tipo_pago,
detalle.concepto_anexo, 
sum(detalle.price_subtotal),
invoice.periodo,
invoice.anexo_94
from account_move_line As detalle , account_move as invoice, res_partner as proveedor
where detalle.move_id = invoice.id and invoice.partner_id = proveedor.id and invoice.anexo_94 is not null
and invoice.type = 'in_invoice' and detalle.account_internal_type = 'other' and invoice.state <> 'draft'
and detalle.exclude_from_invoice_tab = 'f' and detalle.display_type is null and detalle.concepto_anexo > 0
group by proveedor.tipo_persona, proveedor.vat,proveedor.partner_dv,proveedor.name,invoice.tipo_pago,detalle.concepto_anexo,invoice.periodo,invoice.anexo_94 ;


select proveedor.tipo_persona, 
proveedor.vat,
proveedor.partner_dv,
proveedor.name,
invoice.tipo_pago,
detalle.concepto_anexo, 
sum(detalle.price_subtotal),
invoice.periodo
from account_move_line As detalle , account_move as invoice, res_partner as proveedor
where detalle.move_id = invoice.id and invoice.partner_id = proveedor.id 
and invoice.type = 'in_invoice' and detalle.account_internal_type = 'other' and invoice.state <> 'draft'
and detalle.exclude_from_invoice_tab = 'f' and detalle.display_type is null and detalle.concepto_anexo > 0
group by proveedor.tipo_persona, proveedor.vat,proveedor.partner_dv,proveedor.name,invoice.tipo_pago,detalle.concepto_anexo,invoice.periodo;