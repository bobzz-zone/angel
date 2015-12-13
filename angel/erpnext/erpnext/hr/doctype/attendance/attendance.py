# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import getdate, nowdate, cint
from frappe import _
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name

class Attendance(Document):
	def validate_duplicate_record(self):
		res = frappe.db.sql("""select name from `tabAttendance` where employee = %s and att_date = %s
			and name != %s and docstatus = 1""",
			(self.employee, self.att_date, self.name))
		if res:
			frappe.throw(_("Attendance for employee {0} is already marked").format(self.employee))

		set_employee_name(self)

	def check_leave_record(self):
		if self.status == 'Present':
			leave = frappe.db.sql("""select name from `tabLeave Application`
				where employee = %s and %s between from_date and to_date and status = 'Approved'
				and docstatus = 1""", (self.employee, self.att_date))

			if leave:
				frappe.throw(_("Employee {0} was on leave on {1}. Cannot mark attendance.").format(self.employee,
					self.att_date))

	def validate_att_date(self):
		if getdate(self.att_date) > getdate(nowdate()):
			frappe.throw(_("Attendance can not be marked for future dates"))

	def validate_employee(self):
		emp = frappe.db.sql("select name from `tabEmployee` where name = %s and status = 'Active'",
		 	self.employee)
		if not emp:
			frappe.throw(_("Employee {0} is not active or does not exist").format(self.employee))

	def validate(self):
		from erpnext.controllers.status_updater import validate_status
		from erpnext.accounts.utils import validate_fiscal_year
		validate_status(self.status, ["Present", "Absent", "Half Day"])
		validate_fiscal_year(self.att_date, self.fiscal_year, _("Attendance Date"), self)
		self.validate_att_date()
		self.validate_duplicate_record()
		self.check_leave_record()

	def on_update(self):
		# this is done because sometimes user entered wrong employee name
		# while uploading employee attendance
		employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")
		frappe.db.set(self, 'employee_name', employee_name)
                # fingerprint_id is updated from employee value of Employee doctype, whenever employee is selected, fingerprint_id gets updated
		fingerprint_id = frappe.db.get_value("Employee", self.employee, "fingerprint_id")
                frappe.db.set(self, 'fingerprint_id', fingerprint_id)

	def before_save(self):
		self.check_in_time()

	def check_in_time(self):
		clock_in_time = str(self.get("clock_in"))
		clock_out_time = str(self.get("clock_out"))
		hours = str(self.get("hours"))
	
                # Getting Clock In time Detail
		arr_in = clock_in_time.split(":")
 		clock_in_hour = cint(arr_in[0])
		clock_in_min = cint(arr_in[1])
		clock_in_sec = cint(arr_in[2])
		
		# Getting Clock Out Time Detail	
		arr_out = clock_out_time.split(":")
		clock_out_hour = cint(arr_out[0])
		clock_out_min = cint(arr_out[1])
		clock_out_sec = cint(arr_out[2])
	
		# Getting Hours Detail
		arr_hours = hours.split(":")
		if((len(arr_hours) == 3)):
			hours_hour = cint(arr_hours[0])
			hours_min = cint(arr_hours[1])
			hours_sec = cint(arr_hours[2])
			if(not((hours_hour) and (hours_min))):
                        	self.set("status", "Absent")
                	elif((hours_hour < 8 and hours_hour > 0) or (clock_in_hour > 9)):
                        	self.set("status", "Half Day")
                	elif(hours_hour > 8):
                        	self.set("status", "Present")
		elif(not(len(arr_hours))):
			self.set("status", "Absent")

		diff = clock_out_hour - clock_in_hour
		if(diff < 0):
			frappe.throw("Time In Cannot be Greater then Time Out")
		if(clock_in_time == clock_out_time):
			frappe.throw("Time In and Time Out Cannot be Same")
		if((clock_in_hour == 8) and (clock_in_min < 30 and clock_in_min > 1)):
			self.set("fine", 50)
		elif((clock_in_hour == 8) and (clock_in_min < 59)):
			self.set("fine", 100) 	
