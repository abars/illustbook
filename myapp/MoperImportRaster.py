#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#モッパーから静止画像をインポート
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import webapp

import os

import template_select
from google.appengine.ext import webapp
from google.appengine.ext import db

from myapp.MesThread import MesThread
from myapp.Bbs import Bbs
from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8
from myapp.MoperKeyMapper import MoperKeyMapper

class MoperImportRaster (webapp.RequestHandler):
	@staticmethod
	def get_thread(thread_key):
		query=MoperKeyMapper.all().filter("str_thread_key =",thread_key)
		
		mapper=None
		try:
			mapper=query.fetch(limit=1)[0]
		except:
			mapper=MoperKeyMapper()
		if(not mapper.thread):
			mapper.str_thread_key=thread_key
			mapper.thread=db.get(thread_key)
			mapper.put()
		return mapper.thread

	def get(self):
		try:
			thread = MoperImportRaster.get_thread(self.request.get("thread_key"))
			image = thread.image_key
			self.response.headers['Content-Type'] = "application/octet-stream"
			self.response.out.write(image.image)
		except:
			self.response.headers ['Content-type'] = "text/html;charset=utf-8"  
			self.response.out.write("error")