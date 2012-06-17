#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#スレッド構造体
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.ThreadImage import ThreadImage
from myapp.BbsConst import BbsConst

class MesThread(db.Model):
	bbs_key = db.ReferenceProperty(Bbs)
	title = db.TextProperty()
	summary = db.TextProperty()
	image= db.StringProperty()		#******************削除
	image_key=db.ReferenceProperty(ThreadImage)
	author = db.StringProperty()
	mail = db.StringProperty()
	homepage_addr = db.StringProperty()
	comment_cnt = db.IntegerProperty()
	illust_mode=db.IntegerProperty()
	delete_key  = db.StringProperty()
	date = db.DateTimeProperty()
	create_date = db.DateTimeProperty()
	applause_date = db.DateTimeProperty()
	applause = db.IntegerProperty()
	applause_ip = db.StringProperty()
	applause_ip2 = db.StringProperty()
	applause_ip3 = db.StringProperty()
	applause_ip4 = db.StringProperty()
	draw_time=db.IntegerProperty()
	#score=db.ReferenceProperty(RankingScore)
	category = db.StringProperty()
	postscript = db.TextProperty()

	adult = db.IntegerProperty()
	violate_terms = db.IntegerProperty()
	violate_photo = db.IntegerProperty()

	short = db.StringProperty()
	is_png = db.IntegerProperty()
	tag_list = db.StringListProperty()
	bookmark_count = db.IntegerProperty()
	user_id = db.StringProperty()	#Submitter
	is_ipad = db.IntegerProperty()

	cached_image_key = db.StringProperty() #For object cache
	cached_bbs_key = db.StringProperty() #For object cache
	cached_entry_key = db.ListProperty(db.Key) #For object cache
	
	bookmark_comment = db.BlobProperty()

	sand = db.StringProperty()
	
	def put(self,**kwargs):
		super(MesThread, self).put(**kwargs)
		if(self.key()):
			memcache.delete(BbsConst.OBJECT_CACHE_HEADER+str(self.key()))

	def delete(self,**kwargs):
		memcache.delete(BbsConst.OBJECT_CACHE_HEADER+str(self.key()))
		super(MesThread, self).delete(**kwargs)

