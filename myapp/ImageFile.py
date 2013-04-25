#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#キャッシュコントロールして画像を送付
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import logging

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Entry import Entry
from myapp.Bookmark import Bookmark
from myapp.BbsConst import BbsConst

HTTP_DATE_FMT = "%a, %d %b %Y %H:%M:%S GMT"

class ImageFile (webapp.RequestHandler):
	#画像を返す
	def get(self, tag, path, type_name):
		if(path is None):
			self.error(404)
			return
		#type_name=="jpg" or "gif" or "png"
		#tag="thumbnail" or "img"
		ImageFile.serve_file(self,path,type_name,tag)
	
	#コンテンツヘッダを決定する
	@staticmethod
	def get_content_type(type_name):
		if type_name=="gif":
			return "image/gif"
		if type_name=="png":
			return "image/png"
		if type_name=="jpg":
			return "image/jpeg"
		return ""
	
	#コンテンツを供給する
	@staticmethod
	def output_content(p_self, content_date, content_key, content_header, content_blob, serve, tag):
		p_self.response.headers['Content-Type'] = content_header
		last_modified = content_date.strftime(HTTP_DATE_FMT)
		p_self.response.headers['Last-Modified'] = last_modified
		p_self.response.headers['ETag'] = str( tag+'_'+content_key+'_'+str(content_date) )
		if not serve:
			p_self.response.set_status(304) #キャッシュヒットステータス
			return

		p_self.response.out.write(content_blob)
		
	#アイコンを供給
	@staticmethod
	def serve_icon(p_self,bookmark,user_id,size):
		path=user_id

		content=bookmark
		content_key=path
		if(bookmark.date):
			content_date=bookmark.date
		else:
			content_date=datetime.datetime(2010,4,11)
		
		if(size=="mini"):
			content_blob=bookmark.icon_mini
			content_header=str(bookmark.icon_mini_content_type)
		else:
			content_blob=bookmark.icon
			content_header=str(bookmark.icon_content_type)

		tag="icon"

		serve=ImageFile.is_serve(p_self,content_key,content_date,tag)
		ImageFile.output_content(p_self,content_date,content_key,content_header,content_blob, serve, tag)

	@staticmethod
	def create_thumbail(w,h,image,format):
		if(image==None):
			return None

		try:
			img = images.Image(image)
		except:
			return None

		src_w=img.width
		src_h=img.height

		if(h==0):
			img.resize(width=w)
		else:
			img.resize(width=w,height=h)

		code=None

		if(format=="jpeg"):
			try:
				img.execute_transforms()	#exec resize
				code=images.composite([(img, 0, 0, 1.0, images.TOP_LEFT)], img.width, img.height, 0xffffffff, images.JPEG, 90)
			except:
				return None
			content_type='image/jpeg'
		else:
			if(format=="png"):
				try:
					code=img.execute_transforms(output_encoding=images.PNG)
				except:
					return None
				content_type='image/png'
			else:
				return None

		if(code==None):
			return None

		return {"code":code,"width":src_w,"height":src_h,"content_type":content_type}

	@staticmethod
	def _create_thumbnail2_core(content):
		#新規サムネイル作成
		thumb=ImageFile.create_thumbail(200,0,content.image,"jpeg")
		if(thumb==None):
			return False
		content.thumbnail2=thumb["code"]
		if((not content.width) and (not content.height)):	#動画の場合をケア、なくてもいいかも
			content.width=thumb["width"]	#画像サイズを設定
			content.height=thumb["height"]
		try:
			content.put()
			return True
		except:
			logging.error("ImageFile:create_thumbnail:too large image:key:"+str(content.key()))
			return False

	@staticmethod
	def create_thumbnail2(thread):
		#既にサムネイルを作っている
		if thread.thumbnail2_version:
			if thread.thumbnail2_version==BbsConst.THUMBNAIL2_VERSION:
				return

		#動画以外の場合にサムネイルを作成する
		content=thread.image_key
		if not content.gif_thumbnail:
			if(not ImageFile._create_thumbnail2_core(content)):
				return	#作成失敗

		#画像サイズをスレッドに設定
		thread.width=content.width
		thread.height=content.height
		thread.thumbnail2_version=BbsConst.THUMBNAIL2_VERSION
		thread.put()

	@staticmethod
	def get_content(content,tag):
		if(not content):
			return None
		if tag=="icon":
			return (content.icon)
		if tag=="thumbnail":
			if content.gif_thumbnail:
				return (content.gif_thumbnail)
			return (content.thumbnail)
		if tag=="thumbnail2":
			if content.gif_thumbnail:
				return (content.gif_thumbnail)
			return (content.thumbnail2)
		return (content.image)

	#イメージとサムネイルを供給
	@staticmethod
	def serve_file(p_self,path,type_name,tag):
		#キャッシュヒット判定

		#とりあえずmemcacheからヒット判定に必要な要素を取得
		content=None
		
		content_info=memcache.get(BbsConst.IMAGE_CACHE_KEY_AND_DATE+path)
		content_key=None
		content_date=None
		if(content_info):
			content_key=content_info["key"];
			content_date=content_info["date"];

		#memcacheに無ければ新たに取ってくる
		if(content_key is None or content_date is None):
			content=None
			try:
				content = db.get(path)
			except:
				content=None
			if not content:
				p_self.error(404)
				return
			content_key=str(content.key())
			content_date=content.date
			
			memcache.set(BbsConst.IMAGE_CACHE_KEY_AND_DATE+path,{"key":content_key,"date":content_date},BbsConst.IMAGE_CACHE_TIME)

		#サーブするかを決定する
		serve=ImageFile.is_serve(p_self,content_key,content_date,tag)
		if(p_self.request.get("force")):
			serve=True
			if(tag=="thumbnail2"):
				ImageFile._create_thumbnail2_core(db.get(path))

		#サーブする場合、実データを取得
		if(serve and content is None):
			try:
				content = db.get(path)
			except:
				content = None
			if not content:
				p_self.error(404)
				return
		
		#バイナリ取得
		content_blob=ImageFile.get_content(content,tag)
		content_header=ImageFile.get_content_type(type_name)
		if(serve and content_blob==None):
			p_self.error(404)
			return
		ImageFile.output_content(p_self,content_date,content_key,content_header,content_blob, serve, tag)
	
	@staticmethod
	def is_serve(p_self,content_key,content_date,tag):
		#キャッシュヒット判定
		serve = True
		if 'If-Modified-Since' in p_self.request.headers:
			try:
				last_seen = datetime.datetime.strptime(
						p_self.request.headers['If-Modified-Since'],
						HTTP_DATE_FMT)
				if last_seen >= content_date.replace(microsecond=0):
					serve = False
			except:
				serve= True #何らかの理由でModified-Sinceが間違っていた場合は新しくサーブする
		if 'If-None-Match' in p_self.request.headers:
			etags = [x.strip('" ')
							 for x in p_self.request.headers['If-None-Match'].split(',')]
			if ""+tag+"_"+content_key+"_"+str(content_date) in etags:
				serve = False
		return serve
	
	#キャッシュをクリアする
	@staticmethod
	def invalidate_cache(img_id):
		memcache.delete("image_cache_key_"+img_id);
		memcache.delete("image_cache_date_"+img_id);
