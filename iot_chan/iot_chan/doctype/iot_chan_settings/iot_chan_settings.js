// Copyright (c) 2020, dirk and contributors
// For license information, please see license.txt

frappe.ui.form.on('IOT Chan Settings', {
	refresh: function(frm) {
		frm.add_custom_button(__("Synchronous IOT Center"), function() {
			frm.events.sync_iot_center(frm);
		}).removeClass("btn-default").addClass("btn-primary");
	},
	sync_iot_center: function(frm) {
		return frappe.call({
			doc: frm.doc,
			method: "sync_iot_center",
			freeze: true,
			callback: function(r) {
				if(!r.exc) frm.reload_doc();
			}
		})
	}
});
