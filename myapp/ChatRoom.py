#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#チャットルーム
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from myapp.Analyze import Analyze
from myapp.Counter import Counter
from myapp.BbsConst import BbsConst
from myapp.AppCode import AppCode

class ChatRoom(db.Model):
	name = db.StringProperty()
	password = db.StringProperty()
	user_id = db.StringProperty()	#Owner
	user_name = db.StringProperty()
	user_count = db.IntegerProperty()
	command_list = db.TextProperty()
	command_cnt = db.IntegerProperty()
	from_last_update = db.IntegerProperty()
	from_created = db.IntegerProperty()
	thumbnail=db.BlobProperty()
	snap_shot=db.TextProperty()
	snap_range=db.IntegerProperty()
	create_date = 	db.DateTimeProperty(auto_now=False)
	date = db.DateTimeProperty(auto_now=True)
