#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#プロフィールを更新する
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
from myapp.Bookmark import Bookmark
from myapp.ApiObject import ApiObject
from myapp.Pinterest import Pinterest

from myapp.SyncPut import SyncPut

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
		disable_rankwatch =int(self.request.get("disable_rankwatch"))
		regulation=int(self.request.get("regulation"))

		if(name==""):
			Alert.alert_msg_with_write(self,"名前がありません。");
			return

		if(profile==""):
			Alert.alert_msg_with_write(self,"プロフィールがありません。");
			return

		user = users.get_current_user()
		if(not(user)):
			Alert.alert_msg_with_write(self,"ログインが必要です。");
			return
		
		bookmark=ApiObject.get_bookmark_of_user_id_for_write(user.user_id())
		if(bookmark==None):
			Alert.alert_msg_with_write(self,"プロフィールの取得に失敗しました。");
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
		bookmark.disable_rankwatch=disable_rankwatch
		bookmark.regulation=regulation
		
		bookmark.sex=int(self.request.get("sex"))

		if(birthday_year):
			try:
				birthday_year=int(birthday_year)
			except:
				Alert.alert_msg_with_write(self,"生まれた年は半角数字である必要があります。");
				return
		else:
			birthday_year=0

		if(birthday_month):
			try:
				birthday_month=int(birthday_month)
			except:
				Alert.alert_msg_with_write(self,"生まれた月は半角数字である必要があります。");
				return
		else:
			birthday_month=0
		
		if(birthday_day):
			try:
				birthday_day=int(birthday_day)
			except:
				Alert.alert_msg_with_write(self,"生まれた日は半角数字である必要があります。");
				return
		else:
			birthday_day=0
		
		bookmark.birthday_year=birthday_year
		bookmark.birthday_month=birthday_month
		bookmark.birthday_day=birthday_day
		
		bookmark.icon_mini=None	#サムネイルの再作成を要求

		age=Pinterest.get_age(bookmark)
		if(bookmark.regulation and age>=1 and age<=17):
			Alert.alert_msg_with_write(self,"制限付きコンテンツを表示するには18歳以上である必要があります。");
			return


		if(self.request.get("icon")):
			bookmark.icon=db.Blob(self.request.get("icon"))
			img = self.request.body_file.vars['icon']
			bookmark.icon_content_type=img.headers['content-type']
			ApiObject.create_user_thumbnail(bookmark)

		try:
			SyncPut.put_sync(bookmark)
		except:
			Alert.alert_msg_with_write(self,"データストアへの保存に失敗しました。アイコンの容量が1MBを超えている場合は縮小してからアップロードして下さい。");
			return

		self.redirect(str("./mypage"))
		

