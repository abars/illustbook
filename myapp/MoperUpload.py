#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#MOPERデータを新規アップロード
#

import cgi
import os
import sys
import re
import datetime
import random
import logging
import copy

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.Entry import Entry
from myapp.Response import Response
from myapp.MesThread import MesThread
from myapp.BbsConst import BbsConst
from myapp.ThreadImage import ThreadImage
from myapp.SpamCheck import SpamCheck
from myapp.Alert import Alert
from myapp.OwnerCheck import OwnerCheck
from myapp.RecentCommentCache import RecentCommentCache
from myapp.ImageFile import ImageFile
from myapp.ChunkManager import ChunkManager
from myapp.ApiUser import ApiUser

class MoperUpload(webapp.RequestHandler):
	def post(self):
		self.response.headers ['Content-type'] = "text/html;charset=utf-8"  

		try:
			bbs = db.get(self.request.get("bbs_key"))
			user = users.get_current_user()

			if(bbs.bbs_mode==BbsConst.BBS_MODE_ONLY_ADMIN):
				if(OwnerCheck.check(bbs,user)):
					self.response.out.write("[error]")
					return
			
			if(self.request.get("thread_key")):
				thread=db.get(self.request.get("thread_key"))
				timage=thread.image_key
				if(OwnerCheck.check(bbs,user)):
					if(thread.delete_key=="" or thread.delete_key!=self.request.get("delete_key")):
						self.response.out.write("[error]")
						return					
			else:
				timage=ThreadImage()
			
			timage.bbs_key=db.get(self.request.get("bbs_key"))
			timage.image=db.Blob(self.request.get("image"))			
			timage.thumbnail=db.Blob(self.request.get("thumbnail"))			
			
			#削除するチャンクのリスト
			old_chunk_list_key=copy.deepcopy(timage.chunk_list_key)

			#Chunkに分割して入れる
			timage.moper=None
			timage.chunk_list_key=ChunkManager.upload(self.request.get("moper"),db.get(self.request.get("bbs_key")))
			
			timage.gif_thumbnail=db.Blob(self.request.get("gif_thumbnail"))			
			timage.illust_mode=2;

			timage.width=int(self.request.get("canvas_width"))	
			timage.height=int(self.request.get("canvas_height"))	

			timage.put()
			
			ImageFile.invalidate_cache(str(timage.key()))

			self.response.out.write(""+str(timage.key()))		

			#古いデータの削除
			if(old_chunk_list_key):
				ChunkManager.delete(old_chunk_list_key)
		except:
			self.response.out.write("[error]")
			return

		#投稿数の更新
		if(user):
			ApiUser.invalidate_thread_count(user.user_id())
