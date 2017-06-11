frappe.ui.form.on("Combine Deliveries", "onload", function(frm) {
    cur_frm.set_query("delivery_note", function() {
        return {
            "filters": {
                "docstatus": "1",
                "workflow_state":"Siap Kirim"
            }
        };
    });
});