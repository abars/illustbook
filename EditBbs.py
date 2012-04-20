#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#掲示板の編集
#

import os

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db

from Alert import Alert
from Bbs import Bbs
from OwnerCheck import OwnerCheck
from BbsConst import BbsConst
from AppCode import AppCode

class EditBbs(webapp.RequestHandler):
	def get(self):
		try:
			bbs = db.get(self.request.get("bbs_key"))
		except:
			self.response.out.write(Alert.alert_msg("掲示板の編集画面のURLが変更されています。掲示板からログインし、デザインの編集ボタンをクリックして下さい。",self.request.host))
			return
		user = users.get_current_user()
		if(bbs.short!="sample" and OwnerCheck.check(bbs,user)):
			return

		error_str=""
		if self.request.get("error_str"):
			error_str=self.request.get("error_str")
		
		is_css_enable=OwnerCheck.is_admin(user)
		
		is_admin=0
		if(user and OwnerCheck.is_admin(user)):
			is_admin=1

		my_app_list=None
		if(user):
			my_app_list=AppCode.all().filter("user_id =",user.user_id()).filter("mode =",2).fetch(limit=100,offset=0)
		
		template_values = {
			'host': './',
			'bbs': bbs,
			'error_str': error_str,
			'is_css_enable': is_css_enable,
			'is_admin': is_admin,
			'my_app_list': my_app_list,
			'user': user,
			'redirect_url': self.request.path
		}

		path = os.path.join(os.path.dirname(__file__), 'html/portal/general_edit_bbs.html')
		self.response.out.write(template.render(path, template_values))
