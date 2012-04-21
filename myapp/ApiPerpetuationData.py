#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ユーザデータ
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users

from myapp.AppCode import AppCode

class ApiPerpetuationData(db.Model):
	app_key = db.ReferenceProperty(AppCode)
	data_key = db.StringProperty()
	user_id = db.StringProperty()
	text_data = db.TextProperty()
	int_data = db.IntegerProperty()
	date = db.DateTimeProperty(auto_now=True)