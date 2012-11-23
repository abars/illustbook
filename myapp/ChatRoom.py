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
	name = db.StringProperty(indexed=False)
	password = db.StringProperty(indexed=False)
	user_id = db.StringProperty()	#Owner
	user_name = db.StringProperty()
	user_count = db.IntegerProperty()
	command_list = db.TextProperty(indexed=False)
	command_cnt = db.IntegerProperty(indexed=False)
	from_last_update = db.IntegerProperty()
	from_created = db.IntegerProperty()
	thumbnail=db.BlobProperty(indexed=False)
	snap_shot_0=db.TextProperty(indexed=False)
	snap_shot_1=db.TextProperty(indexed=False)
	snap_range=db.IntegerProperty(indexed=False)
	canvas_width=db.IntegerProperty(indexed=False)
	canvas_height=db.IntegerProperty(indexed=False)
	channel_client_list=db.StringListProperty()
	channel_client_list_for_reconnect=db.StringListProperty()
	is_always=db.IntegerProperty()	#for always room search
	create_date = db.DateTimeProperty(auto_now=False)
	date = db.DateTimeProperty(auto_now=True)
