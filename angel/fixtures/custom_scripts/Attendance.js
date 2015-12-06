// fetch value of FingerPrint Id from Employee doctype on change of Employee field automatically

// cur_frm.add_fetch(link_field, source_fieldname, target_fieldname);
cur_frm.add_fetch("employee", "fingerprint_id", "fingerprint_id");

//getting value of fingerprint_id within employee table --> into fingerprint_id of attendance tablle
