# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import datetime
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
		self.validate_attendance()

	def validate_attendance(self):
		early = 0.0
		late  = 0.0
		employee = self.get("employee")
		shift = frappe.db.get_value("Employee", {"name":employee}, "shift")
		if not shift:
			frappe.throw(_("Please set shift for {} employee").format(employee))
			return
		values = frappe.db.get_values("Set Shifts", {"name":shift}, "*", as_dict = True)
		if not values:
			return
		values = values[0]
		start_time = str(values["start_time"])
		end_time = str(values["end_time"])
		clock_in = str(self.get("clock_in"))
		clock_out = str(self.get("clock_out"))
		att_date = str(self.get("att_date"))
		out_date = str(self.get("clockout_date"))
		# Empty Check while upload from upload_attendance
		if (clock_in.find(".") > 0 and clock_out.find(".") > 0):
			self.set("fine", 00)
			self.set("status", "Absent")
			self.set("hours", "00:00:00") 
			self.set("clock_in", clock_in[0:clock_in.find(".")])
			self.set("clock_out", clock_out[0:clock_out.find(".")])
			return
		elif(clock_in.find(".") > 0):
			self.set("fine", 00)
			self.set("status", "Absent")
			self.set("hours", "00:00:00")
			self.set("clock_in", clock_in[0:clock_in.find(".")])
			self.set("clock_out", "00:00:00")
			return
		elif(clock_out.find(".") > 0):
			self.set("fine", 00)
			self.set("status", "Absent")
			self.set("hours", "00:00:00")
			self.set("clock_in", "00:00:00")
			self.set("clock_out", clock_out[0:clock_out.find(".")])
			return
		if(att_date == out_date):
			hours = self.get_time_diff_hours(clock_in, clock_out)
			hour = 0
			if(len(hours.split(":")) != 0):
				arr = hours.split(":")
				hour = cint(arr[0])
			if(hour <= 2 or hour < 0):
				self.set("fine", 00)
				self.set("status", "Absent")
				self.set("clock_in", clock_in)
				self.set("clock_out", clock_out)
				self.set("hours", hours)
				return
			
			clock_in_diff = frappe.utils.time_diff(clock_in, start_time).total_seconds()/3600
			clock_out_diff = frappe.utils.time_diff(end_time, clock_out).total_seconds()/3600

			# Below code will work if employee came in his alloted shift
			if(clock_in_diff > 0 and clock_out_diff > 0):
				total_late_hours = clock_in_diff + clock_out_diff
				if(total_late_hours > 1):
					self.set("fine", 0.00)
					self.set("status", "Half Day")
					self.set("hours", hours)
					self.set("clock_in", clock_in)
					self.set("clock_out", clock_out)
					return
				elif(total_late_hours < 1):
					if(total_late_hours > 0.1 and total_late_hours <= 0.5):
						self.set("fine", 5000)
						self.set("status","Present")
						self.set("hours", hours)
						self.set("clock_in", clock_in)
						self.set("clock_out", clock_out)
						return
					elif(total_late_hours > 0.5 and total_late_hours <= 1):
						self.set("fine", 10000)
						self.set("status", "Present")
						self.set("hours", hours)
						self.set("clock_in", clock_in)
						self.set("clock_out", clock_out)
						return
			# Below code will work if employee came in others shift
			if(clock_in_diff <= 0 and clock_out_diff <= 0):
				self.set("fine", 00)
				self.set("status", "Present")
				self.set("hours", hours)
				self.set("clock_in", clock_in)
				self.set("clock_out", clock_out)
				return 					
			if(clock_in_diff > 0 and clock_out_diff <= 0):
				if(clock_in_diff <= 0.1):
					self.set("fine", 00)
					self.set("status", "Present")
					self.set("hours", hours)
					self.set("clock_in", clock_in)
					self.set("clock_out", clock_out)
					return
				elif(clock_in_diff > 0.1 and clock_in_diff <= 0.5):
					self.set("fine", 5000)
					self.set("status", "Present")
					self.set("hours", hours)
					self.set("clock_in", clock_in)
					self.set("clock_out", clock_out)
					return
				elif(clock_in_diff > 0.5 and clock_in_diff <= 1):
					self.set("fine", 10000)
					self.set("status", "Present")
					self.set("hours", hours)
					self.set("clock_in", clock_in)
					self.set("clock_out", clock_out)
					return
				elif(clock_in_diff > 1):
					self.set("fine", 00)
					self.set("status", "Half Day")
					self.set("hours", hours)
					self.set("clock_in", clock_in)
					self.set("clock_out", clock_out)
					return
			if(clock_out_diff > 0 and clock_in_diff <= 0):
				if(clock_out_diff < 0.5):
					self.set("fine", 00)
					self.set("status", "Present")
					self.set("hours", hours)
					self.set("clock_in", clock_in)
					self.set("clock_out", clock_out)
					return
				elif(clock_out_diff > 0.1 and clock_out_diff <= 0.5):
					self.set("fine", 5000)
					self.set("status", "Present")
					self.set("hours", hours)
					self.set("clock_in", clock_in)
					self.set("clock_out", clock_out)
					return
				elif(clock_out_diff > 0.5 and clock_out_diff <= 1):
					self.set("fine", 10000)
					self.set("status", "Present")
					self.set("hours", hours)
					self.set("clock_in", clock_in)
					self.set("clock_out", clock_out)
					return
				elif(clock_out_diff > 1):
					self.set("fine", 00)
					self.set("status", "Half Day")
					self.set("hours", hours)
					self.set("clock_in", clock_in)
					self.set("clock_out", clock_out)
					return
		elif(att_date != out_date):
			hours = self.time_diff(clock_in, clock_out)
			start_diff = self.calculate_diff(start_time, clock_in)
			end_diff = self.calculate_diff(clock_out, end_time)
			var = self.add_start_end_diff(start_diff, end_diff)
			return self.calculate_attendance(var , clock_in, clock_out, hours)
		
	def get_time_diff_hours(self,clock_in, clock_out):
		clock_in_time = str(clock_in)
		clock_out_time = str(clock_out)
		arr_in = clock_in_time.split(":")
		arr_out = clock_out_time.split(":")
		arr_in_len = len(arr_in)
		arr_out_len = len(arr_out)
		if(arr_in_len != 3 or arr_out_len != 3):
			frappe.throw(_("Please enter time in correct format"))
			return	
		if(clock_in_time == "" or clock_out_time == ""):
			frappe.throw(_("Please set clock in {} and Clock out {} time correctly").format(clock_in_time, clock_out_time))
			return
		hours = ""			
		for t in range(0,3):
			diff = cint(arr_out[t]) - cint(arr_in[t])
			if(t == 0):
				if((diff <= 0 )):
					hours = hours + str((diff))+":"
				elif((diff > 0) and (len(str(diff)) == 2)):
						hours = hours + str(diff) + ":"
				elif((diff > 0) and ((len(str(diff))) == 1)):
					hours = hours + "0" + str(diff) + ":"
			elif(t == 1):
				if((diff < 0)):
					temp_hours = hours.split(":")
					temp_hour = cint(temp_hours[0])
					if(temp_hour < 0):
						temp_hour = temp_hour -1
						minute = 60 - abs(cint(diff))
						hours = str(temp_hour) + ":" + str(minute) + ":"
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
                                	hours = hours + str(abs(diff))
                                elif((diff > 0) and (len(str(diff)) == 2)):
                                        hours = hours + str(diff)      
                                elif((diff > 0) and ((len(str(diff))) == 1)): 
                                        hours = hours + "0" + str(diff)
		return hours
	
	# If There is difference of days
	def time_diff(self, clock_in, clock_out):
		clock_in_time = str(clock_in)
		clock_out_time = str(clock_out)
		clockout_date = self.get("clockout_date")
		clockin_date = self.get("att_date")
		var = clockout_date == clockin_date
		formt = "%Y-%m-%d %H:%M:%S"
		clock_in_datetime = str(clockin_date + " " + clock_in_time)
		clock_out_datetime = str(clockout_date + " " + clock_out_time)
		if not var:
			intime = datetime.datetime.strptime(clock_in_datetime, formt)
			outtime = datetime.datetime.strptime(clock_out_datetime, formt)
			diff = str(outtime - intime)
			if(diff.find(",") >= 0):
				diff = diff[diff.find(",")+1:len(diff)-1]
				return diff
			return diff

	def calculate_diff(self, start_time, clock_in):
		cal_time = ""
		arr_start = start_time.split(":")
		arr_in = clock_in.split(":")
		if(len(arr_start) == 3 and len(arr_in) == 3):
			for t in range(0, 3):
				diff = cint(arr_in[t]) - cint(arr_start[t])
				if(t == 0):
					if(diff < 0):
						cal_time = cal_time + str(24 - abs(diff))
					elif(diff == 0):
						cal_time = cal_time + str(00)
					elif(diff > 0):
						cal_time = cal_time + str(diff)
				elif(t == 1):
					if(cint(cal_time.split(":")[0]) == 0):
						if(diff <= 0):
							cal_time = cal_time + ":00"
						if(diff > 0):
							cal_time = cal_time + ":" + str(diff)
					if(cint(cal_time.split(":")[0]) > 0):
						if(diff < 0):
							hour = cint(cal_time.split(":")[0]) - 1
							min_diff = 60 - abs(diff)
							cal_time = str(hour) + ":" + str(min_diff)
						elif(diff == 0):
							cal_time = cal_time + ":" + str(00)
						elif(diff > 0):
							cal_time = cal_time + ":" + str(diff)
				elif(t ==2):
					cal_time = cal_time + ":" + str(00)
			return cal_time
	#Calculating Time Different:
	def add_start_end_diff(self, start, end):
		frmt = "%H:%M:%S"
		start_time = start
		end_time = end
		start_time_format = datetime.datetime.strptime(start_time, frmt)
		end_time_format = datetime.datetime.strptime(end_time, frmt)
		time1 = datetime.timedelta(hours = start_time_format.hour, minutes = start_time_format.minute, seconds = start_time_format.second)
		time2 = datetime.timedelta(hours = end_time_format.hour, minutes = end_time_format.minute, seconds = end_time_format.second)
		diff = time1 + time2
		diff = diff.total_seconds()/3600
		diff = round(diff, 1)
		return diff
	#Calculating status for different days in attendance
	def calculate_attendance(self, time, clock_in, clock_out, hours):
		time = float(time)
		hours = hours
		arr_hours = hours.split(":")
		hour = cint(arr_hours[0])
		if(hour <= 2):
			self.set("fine", 00)
			self.set("status", "Absent")
			self.set("clock_in", clock_in)
			self.set("clock_out", clock_out)
			self.set("hours", hours)
			return
		if(hour  > 2):
			if(time == 0):
				self.set("fine", 00)
				self.set("status", "Present")
				self.set("clock_in", clock_in)
				self.set("clock_out", clock_out)
				self.set("hours", hours)
				return
			elif(time > 0 and time < 0.5):
				self.set("fine",5000)
				self.set("status", "Present")
				self.set("clock_in", clock_in)
				self.set("clock_out", clock_out)
				self.set("hours", hours)
				return
			elif(time > 0.5 and time < 1):
				self.set("fine", 10000)
				self.set("status", "Present")
				self.set("clock_in", clock_in)
				self.set("clock_out", clock_out)
				self.set("hours", hours)
				return
			elif(time  > 1):
				self.set("fine", 00)
				self.set("status", "Half Day")
				self.set("clock_in", clock_in)
				self.set("clock_out", clock_out)
				self.set("hours", hours)
				return
		
