#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#イベント構造体
#copyright 2014 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from myapp.BbsConst import BbsConst
from myapp.CachedDbModel import CachedDbModel

class Event(CachedDbModel):
	id = db.StringProperty()
	title = db.TextProperty()
	summary = db.TextProperty()
	start_date = db.DateTimeProperty()
	end_date = db.DateTimeProperty()
