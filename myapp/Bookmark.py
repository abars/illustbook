#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ユーザ情報管理構造体
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from myapp.StackFeedData import StackFeedData
from myapp.BbsConst import BbsConst
from myapp.UserIcon import UserIcon

class Bookmark(db.Model):
	owner = db.UserProperty()
	user_id = db.StringProperty()
	feed_list = db.StringListProperty()
	stack_feed_list = db.ListProperty(db.Key)	#自分と他人の投稿情報=home_timeline
	my_timeline = db.ListProperty(db.Key)		#自分の投稿情報=my_timeline
	thread_key_list = db.ListProperty(db.Key)
	bbs_key_list = db.ListProperty(db.Key)
	app_key_list = db.ListProperty(db.Key)
	user_list = db.StringListProperty()	#follow user list
	name = db.StringProperty()
	profile = db.TextProperty()
	
	#アイコン登録直後はここに値が入る
	icon = db.BlobProperty()	#180px
	icon_content_type = db.StringProperty()
	icon_mini = db.BlobProperty()	#50px
	icon_mini_content_type = db.StringProperty()
	thumbnail_created = db.IntegerProperty()
	
	#互換性用
	user_icon = db.ReferenceProperty(UserIcon)

	#削除予定
	thread_list = db.StringListProperty()	#deleted
	bbs_list = db.StringListProperty()	#deleted
	
	#プロフィール情報
	mail = db.StringProperty()
	homepage = db.StringProperty()
	twitter_id = db.StringProperty()
	sex = db.IntegerProperty()
	birthday_year=db.IntegerProperty()
	birthday_month=db.IntegerProperty()
	birthday_day=db.IntegerProperty()
	new_feed_count=db.IntegerProperty()
	disable_rankwatch=db.IntegerProperty()

	sand = db.StringProperty()
	date = db.DateTimeProperty(auto_now=True)

	#ユーザIDベースでキャッシュする
	def put(self,**kwargs):
		super(Bookmark, self).put(**kwargs)
		if(self.key()):
			memcache.delete(BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_BOOKMARK_CACHE_HEADER+self.user_id)

	def delete(self,**kwargs):
		memcache.delete(BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_BOOKMARK_CACHE_HEADER+self.user_id)
		super(Bookmark, self).delete(**kwargs)
