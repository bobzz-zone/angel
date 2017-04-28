// sahil here

$.extend(cur_frm.cscript,{
"after_save": function(doc, cdt, cdn){
        this.frm.refresh();
},

"onload": function(doc, cdt, cdn){

        this.field = cur_frm.get_field("giro_series");
        this.field.grid.df.read_only = 1;
        this.field.grid.refresh();
        var check = doc.__islocal==undefined?true:false;
        if(check){

                this.set_read_only(doc, cdt, cdn);
        }
},

set_read_only: function(doc, cdt, cdn){
                        var me = this;
                        me.frm.toggle_display("generate_giro", 0);
                        me.frm.toggle_display("reset_giro", 0)


},

"generate_giro": function(doc, cdt, cdn){
                        var me = this;
                        var account = me.frm.doc.giro_account;
                        var start_from = cint(me.frm.doc.starting_giro_number);
                        var no_of_cheques = cint(me.frm.doc.no_of_giros);
                        var flag = [];
                        var end = cint(start_from + no_of_cheques);
                        var parent_doc = frappe.model.get_doc("Giro Tracker", me.frm.doc.name);
                        if(!account || !start_from || !no_of_cheques){
                                frappe.msgprint(frappe._("Please enter your data in correct format"));
                                return
                        }
                        var items = doc.giro_series || [];
                        if(items.length > 0){
                                frappe.msgprint(frappe._("Please reset old Enteries before generating new giro list"));
                                return
                        }

                        frappe.call({
                                method: "angel.angel.doctype.giro_tracker.giro_tracker.check_duplicate_entry",
                                args:{"data":doc},
                                callback: function(r){
                                        console.log("Sahil is here");
                                        if(r && r.message){
                                                flag = r.message;
                                                console.log(flag);
                                                console.log(flag.length);
                                                if(flag.length > 0){
                                                        frappe.msgprint(frappe._("Series Already Exists"));
                                                        return
                                                }
                                        }
                                        console.log(flag);
                                        if(flag == ""){
                                                console.log(flag);
                                                console.log(start_from);
                                                console.log(end);
                                                //console.log(parent_doc);
                                                for(var i=start_from; i<end; i++){
                                                        var child_doc = frappe.model.get_new_doc("Giro Series", parent_doc, "giro_series");
                                                        $.extend(child_doc,{
                                                                "giro_number": i,
                                                                "status": "Not Processed",
                                                        });
                                                }
                                        }
                                        me.frm.refresh();
                                }
                        });
                        me.frm.refresh();
        },

"reset_giro": function(doc, cdt, cdn){
                var me = this;
                me.frm.clear_table("giro_series");
                me.frm.refresh();
},

"refresh": function(doc, cdt, cdn){
                var check = doc.__islocal==undefined ? true:false;
                if(check){
                        this.set_read_only(doc, cdt, cdn);
        }
}
});

frappe.ui.form.on("Giro Series",{
"giro_series_add": function(frm, cdt, cdn){
                var item = frm.doc.giro_series;
                frappe.msgprint(frappe._("You cannot add new Giro Number Manually"));
                item.pop();
                frm.refresh();
                return false;

}
});
