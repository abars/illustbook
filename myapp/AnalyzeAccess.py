#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#掲示板のアクセス解析を表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os
import re

import template_select

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users

from myapp.MesThread import MesThread
from myapp.Bbs import Bbs
from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8
from myapp.Alert import Alert
from myapp.Counter import Counter
from myapp.CssDesign import CssDesign

class AnalyzeAccess(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()
		
		page_name=""
		bbs=None

		user=None
		if(page_name==""):
			try:
				bbs = db.get(self.request.get("bbs_key"))
			except:
				bbs=None
			if(bbs==None):
				Alert.alert_msg_notfound(self)
				return

			user = users.get_current_user()
			if(user):
				if(bbs.user_id!=user.user_id()):
					user=None
		
			if(self.request.get("mode")):
				if(self.request.get("mode")=="delete"):
					if(user):
						bbs.analyze.reset()
						bbs.analyze.put()
						Counter.reset_ip(bbs)

			analyze=bbs.analyze.get_referer()
			page_name=bbs.bbs_name;

		analyze=re.sub("\"","\\\"",analyze)
		analyze=re.sub("\'","\\\'",analyze)
		
		show_analyze=False
		if(user or bbs.short=="sample"):
			show_analyze=True
		
		host_url ="./"
		template_values = {
			'host': host_url,
			'bbs': bbs,
			'page_name': page_name,
			'analyze_data':analyze,
			'user': user,
			'show_analyze': show_analyze,
			'is_iphone': CssDesign.is_iphone(self),
			'is_tablet': CssDesign.is_tablet(self),
			'is_english': CssDesign.is_english(self)
			}
		path = '/html/analyze.html'
		self.response.out.write(template_select.render(path, template_values))

