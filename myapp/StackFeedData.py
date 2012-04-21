#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#フィードデータひとつひとつ
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from Bbs import Bbs
from MesThread import MesThread
from BbsConst import BbsConst

class StackFeedData(db.Model):
	feed_mode          = db.StringProperty()
	from_user_id       = db.StringProperty()
	to_user_id         = db.StringProperty()

	user_key           = db.StringProperty()
	bbs_key            = db.ReferenceProperty(Bbs)
	thread_key         = db.ReferenceProperty(MesThread)

	message            = db.TextProperty()
	date               = db.DateTimeProperty(auto_now=True)
	create_date        = db.DateTimeProperty()

	def put(self,**kwargs):
		super(StackFeedData, self).put(**kwargs)
		if(self.key()):
			memcache.delete(BbsConst.OBJECT_CACHE_HEADER+str(self.key()))

	def delete(self,**kwargs):
		memcache.delete(BbsConst.OBJECT_CACHE_HEADER+str(self.key()))
		super(StackFeedData, self).delete(**kwargs)