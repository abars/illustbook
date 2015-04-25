#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#タグ追加
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.MesThread import MesThread
from myapp.MappingThreadId import MappingThreadId
from myapp.Alert import Alert
from myapp.SetUtf8 import SetUtf8
from myapp.RecentTag import RecentTag

class AddTag(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()

		user = users.get_current_user()
		if(not user):
			self.response.out.write(Alert.alert_msg("ログインしている必要があります。",self.request.host));
			return;

		thread=None
		try:
			thread = db.get(self.request.get("thread_key"))	
		except:
			thread=None
		if(not thread):
			self.response.out.write(Alert.alert_msg("スレッドが見つかりません。",self.request.host));
			return

		mode = self.request.get("mode")
		
		if(not thread.tag_list):
			thread.tag_list=[]
		
		tag=self.request.get("tag")
		
		if(tag==""):
			self.response.out.write(Alert.alert_msg("タグを入力して下さい。",self.request.host));
			return;

		if(mode=="add"):
			if(thread.tag_list.count(tag)>0):
				thread.tag_list.remove(tag)
				thread.tag_list.insert(0,tag)
			else:
				thread.tag_list.insert(0,tag)
				tag_info="[Add Tag] "+tag+" "+str(user.user_id())+" "+user.email()
				thread.tag_last_edit=tag
				thread.tag_last_edit_user_id=str(user.user_id())
				logging.info(tag_info)
		else:
			try:
				thread.tag_list.remove(tag)
			except:
				self.response.out.write(Alert.alert_msg("タグ"+tag+"が見つかりません。",self.request.host));
		thread.put()
		
		bbs=db.get(self.request.get("bbs_key"))
		thread=db.get(self.request.get("thread_key"))

		url=MappingThreadId.get_thread_url("./",bbs,thread)
		self.redirect(str(url))
		
