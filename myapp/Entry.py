#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#コメント構造体
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users

from myapp.Bbs import Bbs
from myapp.MesThread import MesThread
from myapp.ThreadImage import ThreadImage
from myapp.CachedDbModel import CachedDbModel

class Entry(CachedDbModel):
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
	last_update_editor = db.StringProperty()	#Deleted(old:for response update to comment cache)
	user_id= db.StringProperty()						#Submitter
	hidden_flag = db.IntegerProperty()	#HiddenComment
	violate_terms = db.IntegerProperty()
	remote_addr = db.StringProperty()
	comment_no = db.IntegerProperty()
	sand = db.StringProperty()
