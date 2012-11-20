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

		#サーブする場合
		if(serve and content is None):
			try:
				content = db.get(path)
			except:
				content = None
			if not content:
				p_self.error(404)
				return
		
		#バイナリ取得
		content_blob=None
		if(content):
			if tag=="icon":
				content_blob=(content.icon)
			else:
				if tag=="thumbnail":
					if content.gif_thumbnail:
						content_blob=(content.gif_thumbnail)
					else:
						content_blob=(content.thumbnail)
				else:
					content_blob=(content.image)

		content_header=ImageFile.get_content_type(type_name)

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
