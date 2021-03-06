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

	thumbnail = db.BlobProperty()	#100px thumbanil(投稿時に生成)(jpeg)
	thumbnail2 = db.BlobProperty()	#200px thumbnail(ImageFileで初期読み込み時に生成)(jpeg)
	tile       = db.BlobProperty()  #144px windows8&webkit icon tile(ImageFileで初期読み込み時の生成)(png)

	moper = db.BlobProperty()			#moperのデータ
	gif_thumbnail = db.BlobProperty()	#moperのサムネイル
	chunk_list = db.StringListProperty()	#deleted
	chunk_list_key = db.ListProperty(db.Key)	#moperに入りきらない場合はここに入る

	width = db.IntegerProperty()	#画像の横幅(Moperの場合は初回、それ以外の場合はthumbnail2の作成時に設定)
	height = db.IntegerProperty()	#画像の高さ(同上）

	illust_mode = db.IntegerProperty()
	date = db.DateTimeProperty(auto_now=True)
