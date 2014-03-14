#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#掲示板のIDが空いているかを確認
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8
from myapp.Alert import Alert
from myapp.CssDesign import CssDesign

class CheckId(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()

		is_english=CssDesign.is_english(self)

		short=self.request.get('id')
		if(MappingId.key_format_check(short)):
			txt="IDは半角英数である必要があります。"
			if(is_english):
				txt="ID must be 16 characters or less"
			Alert.alert_msg_with_write(self,txt)
			return
		if(MappingId.check_capability(short,"")==0):
			txt="ID:"+short+"は既に登録されていて利用できません。"
			if(is_english):
				txt="ID:"+short+" is not available"
			Alert.alert_msg_with_write(self,txt)
			return
		txt="ID:"+short+"は利用可能です。"
		if(is_english):
			txt="ID:"+short+" is available"
		Alert.alert_msg_with_write(self,txt)
