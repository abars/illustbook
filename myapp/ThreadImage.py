#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#スレッドの画像構造体
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users

class ThreadImage(db.Model):
	bbs_key = db.ReferenceProperty()	#どの掲示板のイラストか

	image = db.BlobProperty()		#src image(投稿時に生成)(png or jpeg)(is_png propertyを参照)
	is_png = db.IntegerProperty()	#imageのフォーマット
	width = db.IntegerProperty()	#imageの横幅
	height = db.IntegerProperty()	#imageの高さ

	thumbnail = db.BlobProperty()	#100px thumbanil(投稿時に生成)(jpeg)
	thumbnail2 = db.BlobProperty()	#200px thumbnail(ImageFileで初期読み込み時に生成)(jpeg)
	thumbnail2_version = db.IntegerProperty()	#thumbnail2を生成済みかどうか

	moper = db.BlobProperty()			#moperのデータ
	gif_thumbnail = db.BlobProperty()	#moperのサムネイル
	chunk_list = db.StringListProperty()	#deleted
	chunk_list_key = db.ListProperty(db.Key)	#moperに入りきらない場合はここに入る

	illust_mode = db.IntegerProperty()
	date = db.DateTimeProperty(auto_now=True)
