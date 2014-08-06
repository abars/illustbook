#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#スレッドを編集する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import template_select

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
		try:
			bbs=db.get(self.request.get("bbs_key"));
		except:
			bbs=None

		if(not bbs):
			Alert.alert_msg_with_write(self,"編集する掲示板が見つかりません。")
			return

		try:
			thread = db.get(self.request.get("thread_key"))
		except:
			thread = None

		try:
			entry = db.get(self.request.get("entry_key"))
		except:
			entry = None

		try:
			res = db.get(self.request.get("res_key"))
		except:
			res = None

		if(not thread and not entry and not res):
			Alert.alert_msg_with_write(self,"編集する対象が見つかりません。")
			return

		user = users.get_current_user()
		
		bbs_owner=not OwnerCheck.check(bbs,user)

		thread_owner=False
		if(user):
			if(thread):
				if(user.user_id()==thread.user_id):
					thread_owner=True
			if(entry):
				if(user.user_id()==entry.user_id):
					thread_owner=True
			if(res):
				if(user.user_id()==res.user_id):
					thread_owner=True
		
		if(not bbs_owner and not thread_owner and not OwnerCheck.is_admin(user)):
			Alert.alert_msg_with_write(self,"編集する権限がありません。")
			return
		
		summary=""
		postscript=""
		category=""

		if(thread):
			summary=thread.summary
			if(thread.postscript):
				postscript=thread.postscript
			summary=ReeditEscape.escape(summary);
			postscript=ReeditEscape.escape(postscript);
			category=thread.category

		host_url="./"
		design=CssDesign.get_design_object(self,bbs,host_url,1)
		category_list=CategoryList.get_category_list(bbs)
		
		template_values = {
			'host': './',
			'bbs': bbs,
			'thread': thread,
			'entry': entry,
			'res': res,
			'summary': summary,
			'postscript': postscript,
			'template_path':design["template_path"],
			'css_name':design["css_name"],
			'is_iphone':design["is_iphone"],
			'is_tablet':design["is_tablet"],
			'template_base_color':design["template_base_color"],
			'user': user,
			'redirect_url': self.request.path,
			'edit_thread': True,
			'category_list': category_list,
			'selecting_category': category,
			'res_entry_key': self.request.get("res_entry_key"),
			'is_english': CssDesign.is_english(self)
		}

		path = '/html/edit_thread.html'
		self.response.out.write(template_select.render(path, template_values))
