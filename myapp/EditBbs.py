#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#掲示板のデザインを編集する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os

import template_select

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db

from myapp.Alert import Alert
from myapp.Bbs import Bbs
from myapp.OwnerCheck import OwnerCheck
from myapp.BbsConst import BbsConst
from myapp.AppCode import AppCode
from myapp.CssDesign import CssDesign

class EditBbs(webapp.RequestHandler):
	def get(self):
		try:
			bbs = db.get(self.request.get("bbs_key"))
		except:
			Alert.alert_msg_with_write(self,"掲示板の編集画面のURLが変更されています。掲示板からログインし、デザインの編集ボタンをクリックして下さい。")
			return

		user = users.get_current_user()
		is_admin=0
		if(user and OwnerCheck.is_admin(user)):
			is_admin=1
		if(bbs.short!="sample" and OwnerCheck.check(bbs,user) and not is_admin):
			Alert.alert_msg_with_write(self,"デザインの編集の権限がありません。")
			return

		error_str=""
		if self.request.get("error_str"):
			error_str=self.request.get("error_str")
		
		is_css_enable=OwnerCheck.is_admin(user)
		
		my_app_list=None
		if(user):
			my_app_list=AppCode.all().filter("user_id =",user.user_id()).filter("mode =",2).fetch(limit=100,offset=0)
		
		tab="all"
		if(self.request.get("tab")):
			tab=self.request.get("tab")

		template_values = {
			'host': './',
			'bbs': bbs,
			'error_str': error_str,
			'is_css_enable': is_css_enable,
			'is_admin': is_admin,
			'is_iphone': CssDesign.is_iphone(self),
			'my_app_list': my_app_list,
			'user': user,
			'tab': tab,
			'redirect_url': self.request.path
		}

		path = '/html/edit_bbs.html'
		self.response.out.write(template_select.render(path, template_values))
