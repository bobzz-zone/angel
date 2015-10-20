# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from os import system, getcwd, environ, path
import frappe	

USER = "/home/" + environ['USER'] if environ.has_key("USER") else environ["HOME"]
FBENCH = path.join(USER, "frappe-bench")
APPS = path.join(USER, "frappe-bench/apps")

def after_install():
	frappe.db.set_default('desktop:home_page', '')
        frappe.db.commit()
        # erp-icon.svg  erpnext-footer.png  favicon.png  pos.svg  splash.png   /home/ubuntu/frappe-bench/sites/assets/erpnext/images
        # overright templates/includes/footer/footer_extension.html
        print "===========================Chetan after install===================="
        print getcwd() 
        system("cp " + path.join(APPS, "erpnext/erpnext/templates/includes/footer/footer_extension.html") + " " +  path.join(APPS, "erpnext/erpnext/templates/includes/footer/footer_extension.html-bk"))
        system("cp " + path.join(APPS, "angel/angel/templates/includes/footer/footer_extension.html") + " " + path.join(APPS, "erpnext/erpnext/templates/includes/footer/footer_extension.html"))
        #return 
        system("cp " + path.join(FBENCH, "sites/assets/erpnext/images/erp-icon.svg") + " " + path.join(FBENCH, "sites/assets/erpnext/images/erp-icon-bk.svg"))
        system("cp " + path.join(FBENCH, "sites/assets/erpnext/images/favicon.png ") + " " + path.join(FBENCH, "sites/assets/erpnext/images/favicon-bk.png"))
        system("cp " + path.join(FBENCH, "sites/assets/erpnext/images/splash.png  ") + " " + path.join(FBENCH, "sites/assets/erpnext/images/splash-bk.png"))
        system("cp " + path.join(FBENCH, "sites/assets/angel/images/ocf.svg ") + " " + path.join(FBENCH, "sites/assets/erpnext/images/erp-icon.svg"))
        system("cp " + path.join(FBENCH, "sites/assets/angel/images/favicon-16x16.png ") + " " + path.join(FBENCH, "sites/assets/erpnext/images/favicon.png"))
        system("cp " + path.join(FBENCH, "sites/assets/angel/images/ms-icon-310x310.png ") + " " + path.join(FBENCH, "sites/assets/erpnext/images/splash.png"))

        #overright frappe/frappe/public/js/frappe/ui/toolbar/navbar.html public/html/navbar.html
        #overright  frappe/frappe/public/js/frappe/ui/toolbar/offcanvas_left_sidebar.html public/html/offcanvas_left_sidebar.html    
        #SRC = os.join.path(APPS, "frappe/frappe/public/js/frappe/ui/toolbar/navbar.html")
        
        system("cp " + path.join(APPS, "frappe/frappe/public/js/frappe/ui/toolbar/navbar.html") + " " + path.join(APPS, "frappe/frappe/public/js/frappe/ui/toolbar/navbar.html-bk") )
        system("cp " + path.join(APPS, "frappe/frappe/public/js/frappe/ui/toolbar/offcanvas_left_sidebar.html") + " " + path.join(APPS, "frappe/frappe/public/js/frappe/ui/toolbar/offcanvas_left_sidebar.html-bk"))
        system("cp " + path.join(APPS, "frappe/frappe/templates/pages/desk.html") + " " + path.join(APPS, "frappe/frappe/templates/pages/desk.html-bk") )
        system("cp " + path.join(APPS, "angel/angel/public/html/navbar.html") + " " + path.join(APPS,"frappe/frappe/public/js/frappe/ui/toolbar/navbar.html"))
        system("cp " + path.join(APPS, "angel/angel/public/html/offcanvas_left_sidebar.html") + " " + path.join(APPS, "frappe/frappe/public/js/frappe/ui/toolbar/offcanvas_left_sidebar.html"))
        system("cp " + path.join(APPS, "angel/angel/templates/pages/desk.html") + " " + path.join(APPS, "frappe/frappe/templates/pages/desk.html"))
        #system("cp " + path.join(APPS, "frappe/frappe/public/js/frappe/ui/toolbar/about.js") + " " + path.join(APPS,"frappe/frappe/public/js/frappe/ui/toolbar/about.js-bk"))
        #system("cp " + path.join(APPS, "angel/angel/public/js/about.js") + " " + path.join(APPS, "frappe/frappe/public/js/frappe/ui/toolbar/about.js"))
        # overright ../../erpnext/erpnext/public/js/conf.js ../../angel/angel/public/js/conf.js
        #system("cp " + path.join(APPS, "angel/angel/public/js/conf.js") + " " + path.join(APPS, "erpnext/erpnext/public/js/conf.js"))
	
def def_content_overright(hooks):
        for key in ['default_mail_footer', 'error_report_email', 'website_context']:
		if key in hooks:
			del hooks[key]
	#del hooks['default_mail_footer'] if hooks.has_key('default_mail_footer')
        #del hooks['error_report_email']  if hooks.has_key('error_report_email')
        #del hooks['website_context']     if hooks.has_key('website_context')

def func_name():
        print  str(traceback.extract_stack(None, 2)[0][0]) + ":  " + str(traceback.extract_stack(None, 2)[0][2])

