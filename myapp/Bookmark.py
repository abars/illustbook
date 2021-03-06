#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ユーザ情報管理構造体
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import logging

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from myapp.StackFeedData import StackFeedData
from myapp.BbsConst import BbsConst

class Bookmark(db.Model):
	owner = db.UserProperty()
	user_id = db.StringProperty()
	stack_feed_list = db.ListProperty(db.Key)	#自分と他人の投稿情報=home_timeline
	my_timeline = db.ListProperty(db.Key)		#自分の投稿情報=my_timeline
	thread_key_list = db.ListProperty(db.Key)
	bbs_key_list = db.ListProperty(db.Key)
	app_key_list = db.ListProperty(db.Key)

	user_list = db.StringListProperty()	#follow user list
	follower_list = db.StringListProperty()
	follower_list_enable = db.IntegerProperty()

	name = db.StringProperty()
	profile = db.TextProperty()
	regulation = db.IntegerProperty()	#閲覧モード(1:男性向けマスク、2:女性向けマスク)

	#ミュート
	#mute_bbs_key_list = db.ListProperty(db.Key)	#AppEngineのbugで追加するとfetchがbad_value_errorになる
	#mute_bbs_str_list = db.StringListProperty()
	mute_bbs_packed_str_list = db.TextProperty()	#Listが追加できないので苦肉の策
	mute_user_packed_str_list = db.TextProperty()

	#投稿したイラスト数、投稿時に0クリア
	submit_thread_count = db.IntegerProperty()
	submit_moper_count  = db.IntegerProperty()
	
	#アイコン登録直後はここに値が入る
	icon = db.BlobProperty()	#180px
	icon_content_type = db.StringProperty()
	icon_mini = db.BlobProperty()	#50px
	icon_mini_content_type = db.StringProperty()
	thumbnail_created = db.IntegerProperty()
	
	#互換性用
	#user_icon = db.ReferenceProperty(UserIcon)

	#削除予定
	#feed_list = db.StringListProperty() #削除予定
	#thread_list = db.StringListProperty()	#deleted
	#bbs_list = db.StringListProperty()	#deleted
	
	#プロフィール情報
	mail = db.StringProperty()
	homepage = db.StringProperty()
	twitter_id = db.StringProperty()
	sex = db.IntegerProperty()
	birthday_year=db.IntegerProperty()
	birthday_month=db.IntegerProperty()
	birthday_day=db.IntegerProperty()
	new_feed_count=db.IntegerProperty()	#他のユーザの更新情報の新着数
	new_my_feed_count=db.IntegerProperty()	#自分の更新情報の新着数
	disable_rankwatch=db.IntegerProperty()
	disable_global_tweet=db.IntegerProperty()
	my_color=db.StringProperty()	#マイカラー

	#プライバシー
	privacy_rental_bbs = db.IntegerProperty() #1で非表示
	
	#アカウントの凍結
	frozen = db.IntegerProperty()

	#削除フラグ
	del_flag = db.IntegerProperty()

	sand = db.StringProperty()
	date = db.DateTimeProperty(auto_now=True)

	#mute listのunpack
	def _get_mute_core(self,packed_str_list):
		mute_bbs_list=packed_str_list.split("#")
		ret=[]
		for bbs in mute_bbs_list:
			if(bbs==""):
				continue
			ret.append(bbs)
		return ret

	def get_mute_bbs_list(self):
		if(not self.mute_bbs_packed_str_list):
			return []
		return self._get_mute_core(self.mute_bbs_packed_str_list)

	def get_mute_user_list(self):
		if(not self.mute_user_packed_str_list):
			return []
		return self._get_mute_core(self.mute_user_packed_str_list)

	#ユーザIDベースでキャッシュする
	def put(self,**kwargs):
		super(Bookmark, self).put(**kwargs)
		if(self.key()):
			key=BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_BOOKMARK_CACHE_HEADER+self.user_id
			memcache.delete(key)
			#logging.error("save:"+key)

	def delete(self,**kwargs):
		memcache.delete(BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_BOOKMARK_CACHE_HEADER+self.user_id)
		super(Bookmark, self).delete(**kwargs)

#kay_nameからbookmarkを引く
class BookmarkMapper(db.Model):
	bookmark=db.ReferenceProperty(Bookmark)
	user_id = db.StringProperty()

