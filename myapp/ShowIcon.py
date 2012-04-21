#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ユーザのアイコンを表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import webapp

from myapp.ApiObject import ApiObject
from myapp.ImageFile import ImageFile

class ShowIcon (webapp.RequestHandler):
	def get(self):
		user_id=self.request.get("key")
		bookmark=ApiObject.get_bookmark_of_user_id(user_id)
		if(bookmark==None):
			self.redirect(str("/static_files/empty_user.png"));
			return
		if bookmark.icon:
			ImageFile.serve_icon(self,bookmark,user_id)
		else:
			self.redirect(str("/static_files/empty_user.png"));
			