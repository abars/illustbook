#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#規約違反を報告する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os

import template_select
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db

from myapp.MesThread import MesThread
from myapp.BbsConst import BbsConst
from myapp.Bbs import Bbs
from myapp.SetUtf8 import SetUtf8
from myapp.PageGenerate import PageGenerate
from myapp.MappingId import MappingId
from myapp.ApiFeed import ApiFeed
from myapp.OwnerCheck import OwnerCheck
from myapp.Alert import Alert
from myapp.ApiObject import ApiObject

class ViolationTerms(webapp.RequestHandler):
	def violate_icon(self):
		bookmark=ApiObject.get_bookmark_of_user_id_for_write(self.request.get("user_id"))
		if(bookmark==None):
			Alert.alert_msg_with_write(self,"ブックマークの取得に失敗しました。");
			return
		bookmark.thumbnail_created=BbsConst.USER_ICON_THUMBNAIL_VIOLATE
		bookmark.icon = None
		bookmark.icon_content_type = None
		bookmark.icon_mini = None
		bookmark.icon_mini_content_type = None
		bookmark.put()
		self.redirect("./mypage?user_id="+self.request.get("user_id"))

	def violate_thread(self):
		#スレッド
		thread = db.get(self.request.get("thread_key"))
		
		if(self.request.get("mode")=="adult"):
			if(thread.adult):
				thread.adult=0
			else:
				thread.adult=1

		if(self.request.get("mode")=="terms"):
			if(thread.violate_terms):
				thread.violate_terms=0
			else:
				thread.violate_terms=1
		
		if(self.request.get("mode")=="photo"):
			if(thread.violate_photo):
				thread.violate_photo=0
			else:
				thread.violate_photo=1
			
		if(self.request.get("mode")=="comment"):
			if(thread.prohibit_comment):
				thread.prohibit_comment=0
			else:
				thread.prohibit_comment=1

		thread.put()
		
		ApiFeed.invalidate_cache()

		bbs = db.get(self.request.get("bbs_key"))
		self.redirect(str(MappingId.get_usr_url("./",bbs)+self.request.get("thread_key")+".html"))

	def violate_entry(self):
		#エントリー
		entry=db.get(self.request.get("entry_key"))
		if(entry.violate_terms):
			entry.violate_terms=0
		else:
			entry.violate_terms=1
		entry.put()

		bbs = db.get(self.request.get("bbs_key"))
		self.redirect(str(MappingId.get_usr_url("./",bbs)+self.request.get("thread_key")+".html"))

	def get(self):
		SetUtf8.set()

		user = users.get_current_user()
		if(user):
			if(not OwnerCheck.is_admin(user)):
				Alert.alert_msg_with_write(self,"権限がありません。")
				return

		if(self.request.get("user_id")):
			self.violate_icon()
			return

		if(self.request.get("entry_key")):
			self.violate_entry()
			return

		self.violate_thread()


