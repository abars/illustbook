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

import template_select
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
from myapp.ApiUser import ApiUser

class UpdateThread(webapp.RequestHandler):
	def link_to_profile(self,thread,user):
		link_profile=self.request.get("link_profile")
		if(link_profile):
			if(user):
				if(not thread.user_id):
					thread.user_id=user.user_id()
		else:
			thread.user_id=None

	def update_thread(self,bbs,thread,user):
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
		
		self.link_to_profile(thread,user)

		thread.adult=int(self.request.get("regulation"))

		#thread.hidden_in_list = int(self.request.get('hidden_in_list'))
		
		try:
			thread.comment_cnt = int(self.request.get('comment_cnt'))
		except:
			Alert.alert_msg_with_write(self,"コメント数は数値である必要があります。");
			return True

		thread.search_index_version=0	#インデックス更新
		thread.put()

		if(thread.user_id):
			ApiUser.invalidate_thread_count(thread.user_id)

		return False

	def update_entry(self,entry,user):
		entry.content=cgi.escape(self.request.get("content"))
		entry.editor=self.request.get("editor")
		entry.search_index_version=0	#インデックス更新
		self.link_to_profile(entry,user)
		entry.put()
		return False

	def update_res(self,res,entry,user):
		res.content=cgi.escape(self.request.get("content"))
		res.editor=self.request.get("editor")
		self.link_to_profile(res,user)
		res.put()

		entry.search_index_version=0	#インデックス更新
		entry.put()

		return False

	def post(self):
		bbs=db.get(self.request.get("bbs_key"));

		try:
			thread=db.get(self.request.get("thread_key"))
		except:
			thread=None

		try:
			entry=db.get(self.request.get("entry_key"))
		except:
			entry=None

		try:
			res=db.get(self.request.get("res_key"))
		except:
			res=None
		
		user = users.get_current_user()

		bbs_owner=not OwnerCheck.check(bbs,user)
		thread_owner=False
		if(user):
			if(thread and user.user_id()==thread.user_id):
				thread_owner=True
			if(entry and user.user_id()==entry.user_id):
				thread_owner=True
			if(res and user.user_id()==res.user_id):
				thread_owner=True

		if(not bbs_owner and not thread_owner):
			Alert.alert_msg_with_write(self,"更新する権限がありません。");
			return

		if(thread):
			if(self.update_thread(bbs,thread,user)):
				return
		if(entry):
			if(self.update_entry(entry,user)):
				return
			thread=entry.thread_key
		if(res):
			entry=db.get(self.request.get("res_entry_key"))
			if(self.update_res(res,entry,user)):
				return
			thread=entry.thread_key

		url=MappingThreadId.get_thread_url("./",bbs,thread)
		self.redirect(str(url))

