// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

frappe.provide('frappe.pages');
frappe.provide('frappe.views');

frappe.views.Factory = Class.extend({
	init: function(opts) {
		$.extend(this, opts);
	},
	show: function() {
		var page_name = frappe.get_route_str(),
			me = this;
		if(frappe.pages[page_name] && page_name.indexOf("Form/")===-1) {
			frappe.container.change_to(frappe.pages[page_name]);
			if(me.on_show) {
				me.on_show();
			}
		} else {
			var route = frappe.get_route();
			if(route[1]) {
				me.make(route);
			} else {
				frappe.show_not_found(route);
			}
		}
	},
	make_page: function(double_column, page_name) {
		return frappe.make_page(double_column, page_name);
	}
});

frappe.make_page = function(double_column, page_name) {
	if(!page_name) {
		var page_name = frappe.get_route_str();
	}
	var page = frappe.container.add_page(page_name);

	frappe.ui.make_app_page({
		parent: page,
		single_column: !double_column
	});
	frappe.container.change_to(page_name);
	return page;
}