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
from myapp.CachedDbModel import CachedDbModel

class MesThread(CachedDbModel):
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

	adult = db.IntegerProperty()			#レギュレーション
	violate_terms = db.IntegerProperty()	#規約違反でトップでも個別ページでもイラストを非表示
	violate_photo = db.IntegerProperty()	#トップページに表示しないフラグ、個別ページでは表示する
	prohibit_comment = db.IntegerProperty()	#コメントを禁止

	short = db.StringProperty()
	is_png = db.IntegerProperty()
	tag_list = db.StringListProperty()
	bookmark_count = db.IntegerProperty()
	user_id = db.StringProperty()	#Submitter
	is_ipad = db.IntegerProperty()

	event_id = db.StringProperty()	#Event Id

	cached_image_key = db.StringProperty() #For object cache
	cached_bbs_key = db.StringProperty() #For object cache
	cached_entry_key = db.ListProperty(db.Key) #For object cache
	cached_entry_key_enable = db.BooleanProperty()	#is cached_entry_key is enable
	cached_entry_image_key = db.StringProperty() #For entry image thumbnail
	
	#cached_width = db.IntegerProperty()	#For object cache
	#cached_height = db.IntegerProperty()	#For object cache

	thumbnail2_version = db.IntegerProperty()	#thumbnail2を生成済みかどうか
	width = db.IntegerProperty()	#画像の横幅、thumbnail2を作成するタイミングで代入される
	height = db.IntegerProperty()	#画像の高さ、同上

	search_index_version = db.IntegerProperty()	#サーチ用のインデックスを生成済みかどうか

	bookmark_comment = db.BlobProperty()
	remote_addr = db.StringProperty()

	sand = db.StringProperty()
