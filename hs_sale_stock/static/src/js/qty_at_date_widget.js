odoo.define('hs_sale_stock.QtyAtDateWidget', function (require) {
"use strict";


	const QtyAtDateWidget = require('sale_stock.QtyAtDateWidget');

	QtyAtDateWidget.include({
		_getContent() {
			this.data.alt_qty_available = [];
			/*let alt_qty_available = this.data.alt_qty_available_str || null;
			try {
				if(typeof alt_qty_available == "string"){
					if(alt_qty_available != ""){
						this.data.alt_qty_available = JSON.parse(alt_qty_available);
					}
				}
			} catch (error) {
				console.log("Error al obtener la data desde el backend");
				console.log(error);
			}*/
			return this._super();
		}
	});
});
