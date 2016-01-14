# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe.utils import getdate, nowdate, cint, cstr, flt
from frappe import _
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name

class Attendance(Document):
	ABSENT = _("Absent")
	PRESENT = _("Present")
	HALF_DAY = _("Half Day")
	MIN_FINE = 5000
	MAX_FINE = 10000

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
		start_time = cstr(values["start_time"])
		end_time = cstr(values["end_time"])
		half_day = flt(values["halfday_hours"])
		clock_in = cstr(self.get("clock_in"))
		clock_out = cstr(self.get("clock_out"))
		att_date = cstr(self.get("att_date"))
		out_date = cstr(self.get("clockout_date"))
		# Empty Check while upload from upload_attendance
		if (clock_in.find(".") > 0 and clock_out.find(".") > 0):
			self.set("fine", 00)
			self.set("status", Attendance.ABSENT)
			self.set("hours", 0.0)
			self.set("clock_in", clock_in[0:clock_in.find(".")])
			self.set("clock_out", clock_out[0:clock_out.find(".")])
			return
		elif(clock_in.find(".") > 0):
			self.set("fine", 00)
			self.set("status", Attendance.ABSENT)
			self.set("hours", 0.0)
			self.set("clock_in", clock_in[0:clock_in.find(".")])
			self.set("clock_out", "00:00:00")
			return
		elif(clock_out.find(".") > 0):
			self.set("fine", 00)
			self.set("status", Attendance.ABSENT)
			self.set("hours", 0.0)
			self.set("clock_in", "00:00:00")
			self.set("clock_out", clock_out[0:clock_out.find(".")])
			return
		elif(clock_in == clock_out):
			self.set("fine", 00)
			self.set("status", Attendance.ABSENT)
			self.set("hours", 0.0)
			self.set("clock_in", "00:00:00")
			self.set("clock_out", "00:00:00")
			return
		if(att_date == out_date):
			return self.calculate_attendance_for_same_day(start_time, end_time, clock_in, clock_out, half_day)

		elif(att_date != out_date):
			return self.calculate_attendance_for_different_days(start_time, end_time, clock_in, clock_out, half_day)

    	#Calculate Attendance for Same day
    	def calculate_attendance_for_same_day(self, start_time, end_time, clock_in, clock_out, half_day):
        	clock_in = self.string_to_time_object(clock_in)
        	clock_out = self.string_to_time_object(clock_out)
        	start_time = self.string_to_time_object(start_time)
        	end_time = self.string_to_time_object(end_time)
		half_day = half_day
		total_workable_hour = end_time - start_time
		total_workable_hour_float = total_workable_hour.total_seconds()/3600
        	clock_in_diff = clock_in - start_time
        	clock_out_diff = end_time - clock_out
        	clock_in_diff_in_float = clock_in_diff.total_seconds()/3600
        	clock_out_diff_in_float = clock_out_diff.total_seconds()/3600

        	if((clock_out_diff_in_float > 0 and clock_in_diff_in_float > 0)):
			total_diff = clock_in_diff + clock_out_diff
                 	total_diff_in_float = total_diff.total_seconds()/3600
                 	total_worked_hour = total_workable_hour_float - total_diff_in_float
			if(total_diff_in_float > 0 and total_diff_in_float <= 0.5):
                		self.set("fine", Attendance.MIN_FINE)
                		self.set("status", Attendance.PRESENT)
				self.set("hours", total_worked_hour)
			elif((total_diff_in_float > 0.5 and total_diff_in_float < 1)):
                		self.set("fine", Attendance.MAX_FINE)
                		self.set("status", Attendance.PRESENT)
				self.set("hours", total_worked_hour)
			elif((total_diff_in_float >= 1 and total_worked_hour >= half_day)):
                		self.set("fine", 00)
                		self.set("status", Attendance.HALF_DAY)
				self.set("hours", total_worked_hour)
			else:
				self.set("fine", 00)
				self.set("status", Attendance.ABSENT)
				self.set("hours", total_worked_hour)
		elif((clock_in_diff_in_float > 0 and clock_out_diff_in_float <= 0)):
			total_worked_hour = total_workable_hour_float - clock_in_diff.total_seconds()/3600
			if((clock_in_diff_in_float > 0 and clock_in_diff_in_float <= 0.5)):
                		self.set("fine", Attendance.MIN_FINE)
                		self.set("status", Attendance.PRESENT)
				self.set("hours", total_worked_hour)
			elif((clock_in_diff_in_float > 0.5 and clock_in_diff_in_float < 1)):
                		self.set("fine", Attendance.MAX_FINE)
                		self.set("status", Attendance.PRESENT)
				self.set("hours", total_worked_hour)
			elif((clock_in_diff_in_float >= 1 and total_worked_hour >= half_day)):
                		self.set("fine", 00)
                		self.set("status", Attendance.HALF_DAY)
				self.set("hours", total_worked_hour)
			else:
				self.set("fine", 00)
				self.set("status", Attendance.ABSENT)
				self.set("hours", total_worked_hour)
		elif((clock_in_diff_in_float <= 0 and clock_out_diff_in_float > 0)):
			total_worked_hour = total_workable_hour_float - clock_out_diff.total_seconds()/3600
			if((clock_out_diff_in_float > 0 and clock_out_diff_in_float  <= 0.5)):
                		self.set("fine", Attendance.MIN_FINE)
                		self.set("status", Attendance.PRESENT)
				self.set("hours", total_worked_hour)
			elif((clock_out_diff_in_float > 0.5 and clock_out_diff_in_float  < 1)):
                		self.set("fine", Attendance.MAX_FINE)
                		self.set("status", Attendance.PRESENT)
				self.set("hours", total_worked_hour)
				elif((clock_out_diff_in_float >= 1 and total_worked_hour >= half_day)):
                		self.set("fine", 00)
                		self.set("status", Attendance.HALF_DAY)
				self.set("hours", total_worked_hour)
			else:
				self.set("fine" ,00)
				self.set("status", Attendance.ABSENT)
				self.set("hours", total_worked_hour)
		elif(clock_out_diff_in_float <= 0 and clock_in_diff_in_float <= 0):
            		self.set("fine", 00)
            		self.set("status", Attendance.PRESENT)
			self.set("hours", total_workable_hour_float)
		else:
			self.set("fine", 00)
			self.set("status", Attendnace.ABSENT)
			self.set("hours", 0.0)


    	#Calculating Attendance for Differet Days
    	def calculate_attendance_for_different_days(self, start_time, end_time, clock_in, clock_out, half_day):
		start_time = self.string_to_time_object(start_time)
		end_time = self.string_to_time_object(end_time)
		clock_in = self.string_to_time_object(clock_in)
		clock_out  = self.string_to_time_object(clock_out)
		half_day = half_day
		DAY = "23:59:59"
		DAY = self.string_to_time_object(DAY)
		clock_in_diff = None
		if(end_time >= clock_in):
			clock_in_diff = clock_in - start_time + DAY
		else:
			clock_in_diff = clock_in - start_time
		clock_out_diff = end_time - clock_out
		clock_in_diff_in_float = clock_in_diff.total_seconds()/3600
		clock_out_diff_in_float = clock_out_diff.total_seconds()/3600
		total_workable_hour = self.string_to_time_object(self.time_diff(start_time, end_time))
		total_workable_hour_in_float = total_workable_hour.total_seconds()/3600
		if(clock_in_diff_in_float > 0 and clock_out_diff_in_float > 0):
			total_diff = clock_in_diff_in_float + clock_out_diff_in_float
			total_worked = total_workable_hour_in_float - total_diff
			if((total_diff > 0 and total_diff < 0.5)):
				self.set("fine", Attendance.MIN_FINE)
				self.set("status", Attendance.PRESENT)
				self.set("hours", total_worked)
			elif((total_diff > 0.5 and total_diff < 1)):
				self.set("fine", Attendance.MAX_FINE)
				self.set("status", Attendance.PRESENT)
				self.set("hours", total_worked)
			elif((total_diff >= 1 and total_diff >= half_day and total_worked >= half_day)):
				self.set("fine", 00)
				self.set("status", Attendance.HALF_DAY)
				self.set("hours", total_worked)
			else:
				self.set("fine", 00)
				self.set("status", Attendance.ABSENT)
				self.set("hours", total_worked)
		elif(clock_in_diff_in_float > 0 and clock_out_diff_in_float <= 0):
			total_worked = total_workable_hour_in_float - clock_in_diff_in_float
			if(clock_in_diff_in_float > 0 and clock_in_diff_in_float <= 0.5):
				self.set("fine", Attendance.MIN_FINE)
				self.set("status", Attendance.PRESENT)
				self.set("hours", total_worked)
			elif(clock_in_diff_in_float > 0.5 and clock_in_diff_in_float < 1):
				self.set("fine", Attendance.MAX_FINE)
				self.set("status", Attendance.PRESENT)
				self.set("hours", total_worked)
			elif((clock_in_diff_in_float >= 1 and total_worked >= half_day)):
				self.set("fine", 00)
				self.set("status", Attendance.HALF_DAY)
				self.set("hours", total_worked)
			else:
				self.set("fine", 00)
				self.set("status", Attendance.ABSENT)
				self.set("hours", total_worked)
		elif(clock_out_diff_in_float > 0 and clock_in_diff_in_float <= 0):
			total_worked = total_workable_hour_in_float - clock_out_diff_in_float
			if(clock_out_diff_in_float > 0 and clock_out_diff_in_float <= 0.5):
				self.set("fine", Attendance.MIN_FINE)
				self.set("status", Attendance.PRESENT)
				self.set("hours",total_worked)
			elif(clock_out_diff_in_float > 0.5 and clock_out_diff_in_float < 1):
				self.set("fine", Attendance.MAX_FINE)
				self.set("status", Attendance.PRESENT)
				self.set("hours", total_worked)
			elif((clock_out_diff_in_float >= 1 and total_worked >= half_day)):
				self.set("fine", 00)
				self.set("status", Attendance.HALF_DAY)
				self.set("hours", total_worked)
			else:
				self.set("fine", 00)
				self.set("status", Attendance.ABSENT)
				self.set("hours", total_worked)
		elif(clock_out_diff_in_float <= 0 and clock_in_diff_in_float <= 0):
			self.set("fine", 00)
			self.set("status", Attendance.PRESENT)
			self.set("hours", total_workable_hour_in_float)
		else:
			self.set("fine", 00)
			self.set("status", Attendance.ABSENT)
			self.set("hours", 0.0)

	#Calculate Time If There is difference of days
	def time_diff(self, clock_in, clock_out):
		clock_in_time = cstr(clock_in)
		clock_out_time = cstr(clock_out)
		clockout_date = self.get("clockout_date")
		clockin_date = self.get("att_date")
		var = clockout_date == clockin_date
		formt = "%Y-%m-%d %H:%M:%S"
	        time_format = "%H:%M:%S"
		clock_in_datetime = cstr(clockin_date + " " + clock_in_time)
		clock_out_datetime = cstr(clockout_date + " " + clock_out_time)
		if not var:
			intime = datetime.datetime.strptime(clock_in_datetime, formt)
			outtime = datetime.datetime.strptime(clock_out_datetime, formt)
			diff = cstr(outtime - intime)
			if(diff.find(",") >= 0):
				diff = diff[diff.find(",")+1:len(diff)].strip()
			return diff.strip()
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
						cal_time = cal_time + cstr(24 - abs(diff))
					elif(diff == 0):
						cal_time = cal_time + cstr(00)
					elif(diff > 0):
						cal_time = cal_time + cstr(diff)
				elif(t == 1):
					if(cint(cal_time.split(":")[0]) == 0):
						if(diff <= 0):
							cal_time = cal_time + ":00"
						if(diff > 0):
							cal_time = cal_time + ":" + cstr(diff)
					if(cint(cal_time.split(":")[0]) > 0):
						if(diff < 0):
							hour = cint(cal_time.split(":")[0]) - 1
							min_diff = 60 - abs(diff)
							cal_time = cstr(hour) + ":" + cstr(min_diff)
						elif(diff == 0):
							cal_time = cal_time + ":" + cstr(00)
						elif(diff > 0):
							cal_time = cal_time + ":" + cstr(diff)
				elif(t ==2):
					cal_time = cal_time + ":" + cstr(00)
			return cal_time



    	def string_to_time_object(self, string_time):
        	string_time = string_time
        	time_format = "%H:%M:%S"
        	#converting String to Time Format
        	format_time = datetime.datetime.strptime(string_time, time_format)
        	#Converting to Time Object
        	time_object = datetime.timedelta(hours = format_time.hour, minutes = format_time.minute, seconds = format_time.second)
        	return time_object	
