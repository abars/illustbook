#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#スレッドを編集する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

import re
import os

from myapp.Bbs import Bbs
from myapp.MesThread import MesThread
from myapp.OwnerCheck import OwnerCheck
from myapp.Alert import Alert
from myapp.CssDesign import CssDesign
from myapp.ReeditEscape import ReeditEscape
from myapp.CategoryList import CategoryList

class EditThread(webapp.RequestHandler):
	def get(self):
		bbs=db.get(self.request.get("bbs_key"));
		user = users.get_current_user()
		if(OwnerCheck.check(bbs,user)):
			self.response.out.write(Alert.alert_msg("編集する権限がありません。",self.request.host))
			return
		thread = db.get(self.request.get("thread_key"))
		
		summary=thread.summary
		postscript=""
		if(thread.postscript):
			postscript=thread.postscript
		
		summary=ReeditEscape.escape(summary);
		postscript=ReeditEscape.escape(postscript);
		
		host_url="./"
		design=CssDesign.get_design_object(self,bbs,host_url,1)

		category_list=CategoryList.get_category_list(bbs)
		
		template_values = {
			'host': './',
			'bbs': bbs,
			'thread': thread,
			'summary': summary,
			'postscript': postscript,
			'template_path':design["template_path"],
			'css_name':design["css_name"],
			'is_iphone':design["is_iphone"],
			'template_base_color':design["template_base_color"],
			'user': user,
			'redirect_url': self.request.path,
			'edit_thread': True,
			'category_list': category_list,
			'selecting_category': thread.category
		}

		path = os.path.join(os.path.dirname(__file__), '../html/edit_thread.html')
		self.response.out.write(template.render(path, template_values))
