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

from Bbs import Bbs
from Entry import Entry
from Response import Response
from MesThread import MesThread
from BbsConst import BbsConst
from ThreadImage import ThreadImage
from SpamCheck import SpamCheck
from Alert import Alert
from OwnerCheck import OwnerCheck
from MappingId import MappingId
from MappingThreadId import MappingThreadId

class UpdateThread(webapp.RequestHandler):
	def post(self):
		bbs=db.get(self.request.get("bbs_key"));
		user = users.get_current_user()
		if(OwnerCheck.check(bbs,user)):
			self.response.out.write(Alert.alert_msg("スレッドを更新する権限がありません。",self.request.host));
			return
		thread=db.get(self.request.get("thread_key"));

		title = self.request.get('thread_title')
		title = cgi.escape(title)
		compiled_line = re.compile("\r\n|\r|\n")
		title = compiled_line.sub(r'<br>', title)
		thread.title = title
		
		thread.author=self.request.get('thread_author')
		
		category = self.request.get("category")
		thread.category=category

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
			self.response.out.write(Alert.alert_msg("コメント数は数値である必要があります。",self.request.host));
			return

		thread.put()
		url=MappingThreadId.get_thread_url("./",bbs,thread)
		self.redirect(str(url))

