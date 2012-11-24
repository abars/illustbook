#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#スレッドを更新する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.Entry import Entry
from myapp.Response import Response
from myapp.MesThread import MesThread
from myapp.BbsConst import BbsConst
from myapp.ThreadImage import ThreadImage
from myapp.SpamCheck import SpamCheck
from myapp.Alert import Alert
from myapp.OwnerCheck import OwnerCheck
from myapp.MappingId import MappingId
from myapp.MappingThreadId import MappingThreadId
from myapp.CategoryList import CategoryList

class UpdateThread(webapp.RequestHandler):
	def post(self):
		bbs=db.get(self.request.get("bbs_key"));
		thread=db.get(self.request.get("thread_key"));
		user = users.get_current_user()

		bbs_owner=not OwnerCheck.check(bbs,user)
		thread_owner=False
		if(user and user.user_id()==thread.user_id):
			thread_owner=True
		
		if(not bbs_owner and not thread_owner):
			Alert.alert_msg_with_write(self,"スレッドを更新する権限がありません。");
			return

		title = self.request.get('thread_title')
		title = cgi.escape(title)
		compiled_line = re.compile("\r\n|\r|\n")
		title = compiled_line.sub(r'<br>', title)
		thread.title = title
		
		thread.author=self.request.get('thread_author')
		
		category = self.request.get("thread_category")
		thread.category=category
		CategoryList.add_new_category(bbs,category)

		summary = self.request.get('thread_summary')
		summary = compiled_line.sub(r'', summary)
		thread.summary = summary

		postscript = self.request.get('thread_postscript')
		postscript = compiled_line.sub(r'', postscript)
		thread.postscript = postscript
		
		link_profile=self.request.get("link_profile")
		if(link_profile):
			if(user):
				if(not thread.user_id):
					thread.user_id=user.user_id()
		else:
			thread.user_id=None

		#thread.hidden_in_list = int(self.request.get('hidden_in_list'))
		
		try:
			thread.comment_cnt = int(self.request.get('comment_cnt'))
		except:
			Alert.alert_msg_with_write(self,"コメント数は数値である必要があります。");
			return

		thread.put()
		url=MappingThreadId.get_thread_url("./",bbs,thread)
		self.redirect(str(url))

