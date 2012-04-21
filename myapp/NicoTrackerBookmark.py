#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ニコニコトラッカーのパーソナライズ
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users

class NicoTrackerBookmark(db.Model):
	user_id = db.StringProperty()
	bookmark_id_list = db.StringListProperty()
	bookmark_title_list = db.StringListProperty()
	date = db.DateTimeProperty(auto_now=True)

