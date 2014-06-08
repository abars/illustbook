#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ユーザのアイコンを表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import base64

from google.appengine.ext import webapp
from google.appengine.ext import db

from myapp.ApiObject import ApiObject
from myapp.ImageFile import ImageFile
from myapp.Bookmark import Bookmark

class ShowIcon (webapp.RequestHandler):
	def get(self):
		user_id=self.request.get("key")

		bookmark=ApiObject.get_bookmark_of_user_id(user_id)
		if(bookmark==None):
			self.redirect(str("/static_files/empty_user.png"));
			return
		
		size="big"
		if(self.request.get("size") and self.request.get("size")=="mini"):
			size="mini"
		
		if(not bookmark.icon):
			white_png=db.Blob(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP4/x8AAwAB/2+Bq7YAAAAASUVORK5CYII="))
			bookmark.icon=white_png
			bookmark.icon_mini=white_png
			bookmark.icon_content_type="image/png"
			bookmark.icon_mini_content_type="image/png"

		if(bookmark.icon):
			ImageFile.serve_icon(self,bookmark,user_id,size)
		else:
			self.redirect(str("/static_files/empty_user.png"));
