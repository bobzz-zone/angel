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
		clock_in = self.get("clock_in")
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
		clock_out_default = clock_out_time.find(".")
		clock_in_default = clock_in_time.find(".")
		arr_in = clock_in_time.split(":")
                arr_out = clock_out_time.split(":")
		arr_in_len = len(arr_in)
		arr_out_len = len(arr_out)	
	
		if((clock_out_default > 0 and  clock_in_default > 0)):	
			self.set("status", "Absent")
			self.set("clock_in", "00:00:00")
			self.set("clock_out", "00:00:00")
			self.set("hours", "00:00:00")
			self.set("fine", 0.0)
			return
		elif((clock_in_default < 0) and (clock_out_default > 0)):
			self.set("clock_in", self.get("clock_in"))
			self.set("status", "Absent")
			self.set("clock_out", "00:00:00")
			self.set("hours","00:00:00")
			return
		elif((clock_out_default < 0) and (clock_in_default > 0)):
			self.set("clock_out", self.get("clock_out"))
			self.set("status", "Absent")
			self.set("clock_in", "00:00:00")
			self.set("hours", "00:00:00")
			return
		elif(clock_out_default < 0 and clock_in_default < 0):
			hours = ""			
			for t in range(0,3):
				diff = cint(arr_out[t]) - cint(arr_in[t])
				if(t == 0):
					if((diff <= 0 )):
						hours = hours + "00:"
					elif((diff > 0) and (len(str(diff)) == 2)):
						hours = hours + str(diff) + ":"
					elif((diff > 0) and ((len(str(diff))) == 1)):
						hours = hours + "0" + str(diff) + ":"
				elif(t == 1):
					if((diff < 0)):
						temp_hours = hours.split(":")
						temp_hour = cint(temp_hours[0])
						if(temp_hour == 0):
							temp_diff = str(diff).replace("-", "", 1)
							temp_diff = cint(temp_diff)
							temp_diff = 60 - temp_diff
							hours = hours + str(temp_diff) + ":"
						elif(temp_hour != 0):
							temp_diff = 60 - int(str(diff).replace("-", "", 1))
							temp_hour = temp_hour - 1
							temp_hour_str = str(temp_hour)
							if((len(temp_hour_str)) == 1):
								hours = "0" + str(temp_hour) + ":" + str(temp_diff) + ":"
							elif((len(temp_hour_str)) == 2):
 								hours =  str(temp_hour) + ":" + str(temp_diff) + ":"
					elif(diff == 0):
						hours = hours + "00:"	
                                        elif((diff > 0) and (len(str(diff)) == 2)):
                                                hours = hours + str(diff) + ":"      
                                        elif((diff > 0) and ((len(str(diff))) == 1)): 
                                                hours = hours + "0" + str( diff) + ":"
				elif(t == 2):
					if((diff <= 0 )):
                                                hours = hours + "00"
                                        elif((diff > 0) and (len(str(diff)) == 2)):
                                                hours = hours + str(diff)      
                                        elif((diff > 0) and ((len(str(diff))) == 1)): 
                                                hours = hours + "0" + str(diff)
			self.set("hours", hours)
			hours_arr = self.get("hours").split(":")
			arr_in_hour = cint(arr_in[0])
			arr_in_min = cint(arr_in[1])
			arr_out_hour = cint(arr_out[0])
			arr_out_min = cint(arr_out[0])
			hours_hour = cint( hours_arr[0])
			hours_min = cint(hours_arr[1])
			if((arr_in_hour == 8) and (arr_in_min > 31 and arr_in_min <= 59)):
				self.set("fine", 5000)
				if(hours_hour >= 8 and (hours_min >= 30) or (hours_hour > 8)):
					self.set("status", "Present")
	
			elif((arr_in_hour <= 8 and arr_in_min <= 30) or (arr_in_hour < 8)):
                                if((hours_hour > 8) or (hours_hour >= 8 and hours_min >= 30)):
                                        self.set("status", "Present")
                                        self.set("fine", 00)

			elif((arr_in_hour == 9) and (arr_in_min > 1 and arr_in_min <= 30)):
				self.set("fine", 10000)
				if((hours_hour >= 8 and hours_min >= 30) or (hours > 8)):
					self.set("status", "Present")
					
			elif(((arr_in_hour >= 9) and (arr_in_min >= 31)) or (arr_in_hour  > 9)):
				self.set("status", "Half Day")
				self.set("fine", 00)
			
			if(hours_hour < 8 and hours_hour > 4):
				self.set("status", "Half Day")
				self.set("fine", 00)

