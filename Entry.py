#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#コメント構造体
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users

from Bbs import Bbs
from MesThread import MesThread
from ThreadImage import ThreadImage

class Entry(db.Model):
	bbs_key = db.ReferenceProperty(Bbs)
	thread_key = db.ReferenceProperty(MesThread)
	editor = db.StringProperty()
	mail = db.StringProperty()
	homepage_addr = db.StringProperty()
	content = db.TextProperty()
	image = db.BlobProperty()
	thumbnail = db.BlobProperty()
	del_flag =  db.IntegerProperty()
	res_list=db.ListProperty(item_type=db.Key)	
	create_date = db.DateTimeProperty()
	date = db.DateTimeProperty(auto_now=False)
	illust_reply = db.IntegerProperty()
	illust_reply_image = db.StringProperty()	#Deleted
	illust_reply_image_key = db.ReferenceProperty(ThreadImage)
	last_update_editor = db.StringProperty()	#for response update to comment cache
	user_id= db.StringProperty()						#Submitter
	hidden_flag = db.IntegerProperty()	#HiddenComment