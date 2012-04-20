#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#プロフィールを更新
#

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
from MesThread import MesThread
from MappingThreadId import MappingThreadId
from Alert import Alert
from SetUtf8 import SetUtf8
from RecentTag import RecentTag
from Bookmark import Bookmark
from ApiObject import ApiObject

from SyncPut import SyncPut

class UpdateProfile(webapp.RequestHandler):
	def post(self):
		SetUtf8.set()

		mode = self.request.get("mode")
		name = self.request.get("name")
		profile = self.request.get("profile")
		homepage = self.request.get("homepage")
		mail = self.request.get("mail")
		twitter = self.request.get("twitter")
		birthday_year = self.request.get("birthday_year")
		birthday_month = self.request.get("birthday_month")
		birthday_day = self.request.get("birthday_day")

		if(name==""):
			self.response.out.write(Alert.alert_msg("名前がありません。",self.request.host));
			return

		if(profile==""):
			self.response.out.write(Alert.alert_msg("プロフィールがありません。",self.request.host));
			return

		user = users.get_current_user()
		if(not(user)):
			self.response.out.write(Alert.alert_msg("ログインが必要です。",self.request.host));
			return
		
		bookmark=ApiObject.get_bookmark_of_user_id_for_write(user.user_id())
		if(bookmark==None):
			self.response.out.write(Alert.alert_msg("プロフィールの取得に失敗しました。",self.request.host));
			return
		
		profile = cgi.escape(profile)
		compiled_line = re.compile("\r\n|\r|\n")
		profile = compiled_line.sub(r'<br>', profile)

		if(mail=="None"):
			mail=""
		if(homepage=="None"):
			homepage=""
		if(twitter=="None"):
			twitter=""

		bookmark.name=name
		bookmark.profile=profile
		bookmark.mail=mail
		bookmark.twitter_id=twitter
		bookmark.homepage=homepage
		bookmark.owner=user
		
		bookmark.sex=int(self.request.get("sex"))

		if(birthday_year):
			try:
				birthday_year=int(birthday_year)
			except:
				self.response.out.write(Alert.alert_msg("生まれた年は半角数字である必要があります。",self.request.host));
				return
		else:
			birthday_year=0

		if(birthday_month):
			try:
				birthday_month=int(birthday_month)
			except:
				self.response.out.write(Alert.alert_msg("生まれた月は半角数字である必要があります。",self.request.host));
				return
		else:
			birthday_month=0
		
		if(birthday_day):
			try:
				birthday_day=int(birthday_day)
			except:
				self.response.out.write(Alert.alert_msg("生まれた日は半角数字である必要があります。",self.request.host));
				return
		else:
			birthday_day=0
		
		bookmark.birthday_year=birthday_year
		bookmark.birthday_month=birthday_month
		bookmark.birthday_day=birthday_day
		
		if(self.request.get("icon")):
			bookmark.icon=db.Blob(self.request.get("icon"))
			img = self.request.body_file.vars['icon']
			bookmark.icon_content_type=img.headers['content-type']
			ApiObject.create_user_thumbnail(bookmark)
		
		#bookmark.put()
		SyncPut.put_sync(bookmark)
		
		self.redirect(str("./mypage"))
		

