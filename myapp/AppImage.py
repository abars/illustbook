#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#イラストブックアプリのユーザアップロード画像
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

from Entry import Entry
from ImageFile import ImageFile
from AppPortal import AppPortal

class AppImage (webapp.RequestHandler):
	def get(self, app_id, image_id,):
		if(app_id is None):
			self.error(404)
			return
		app=AppPortal.get_app(app_id)
		if(app is None):
			self.error(404)
			return
		
		index_no=app.image_id_list.index(image_id)
		blob=app.image_blob_list[index_no];
		content_type=app.image_type_list[index_no];
		
		self.response.headers['Content-Type']=content_type
		self.response.out.write(blob)
		
