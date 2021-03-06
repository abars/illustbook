#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#一時領域にイラストを保存
#
#ネイティブアプリからアップロードする場合は、
#一時領域にイラストを保存後、任意の掲示板にアップロードする
#
#copyright 2013 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import time
import datetime
import random
import logging
import base64

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
from myapp.MappingThreadId import MappingThreadId
from myapp.Bookmark import Bookmark
from myapp.UTC import UTC
from myapp.JST import JST
from myapp.StackFeed import StackFeed
from myapp.SyncPut import SyncPut
from myapp.ApiFeed import ApiFeed
from myapp.CategoryList import CategoryList
from myapp.EscapeComment import EscapeComment
from myapp.RssFeed import RssFeed
from myapp.ApiUser import ApiUser
from myapp.TempImage import TempImage
from myapp.CssDesign import CssDesign
from myapp.ApiBookmark import ApiBookmark
from myapp.ShowEntry import ShowEntry
from myapp.MappingId import MappingId

class UploadTemp(webapp.RequestHandler):
	@staticmethod
	def get_sec(now):
		return int(time.mktime(now.timetuple()))

	def delete_old_temp_image(self):
		temp_image_list=TempImage.all().order("-date").fetch(limit=10)		
		for temp_image in temp_image_list:
			from_last_update=(UploadTemp.get_sec(datetime.datetime.now())-UploadTemp.get_sec(temp_image.date))/60
			if(from_last_update>=60):
				temp_image.delete()

	def post(self):
		self.delete_old_temp_image()

		timage = TempImage()		
		timage.image=db.Blob(self.request.get("image"))
		timage.thumbnail=db.Blob(self.request.get("thumbnail"))
		timage.date=datetime.datetime.today()
		if(self.request.get("args")):
			timage.args=self.request.get("args")
		else:
			timage.args=None

		timage.put()

		self.response.headers ['Content-type'] = "text/html;charset=utf-8";
		return_code="success&"+str(timage.key())
		self.response.out.write(return_code);

		#logging.error(return_code)
	
	def get_target_bbs(self,args):
		#args="ilbpaint://bbs_key=ahNkZXZ-aWxsdXN0LWJvb2staHJkchALEgNCYnMYgICAgODhtAkM"
		if(not args):
			return None
		list=args.split("bbs_key=")
		if(len(list)>=2):
			bbs_key=list[1]
			bbs=db.get(bbs_key)
			target_bbs={
			"title":bbs.bbs_name,
			"key":bbs_key
			}
			bbs_list=[]
			bbs_list.append(target_bbs)
			return bbs_list
		return None

	def get(self):
		user = users.get_current_user()
		user_name=ShowEntry.get_user_name(user)

		bbs_list=[]

		if(user):
			user_id=user.user_id()
			
			bookmark_bbs_list=ApiBookmark.bookmark_get_bbs_list(self,user_id)
			rental_bbs_list=ApiUser.user_get_bbs_list(self,user_id)
			
			if(rental_bbs_list):
				bbs_list.extend(rental_bbs_list)
			if(bookmark_bbs_list):
				bbs_list.extend(bookmark_bbs_list)

			sample_bbs={
			"title":"サンプルお絵描き掲示板",
			"key":MappingId.mapping("sample")
			}
			bbs_list.append(sample_bbs)

		temp_key=self.request.get("temp_key")

		args=None
		if(temp_key):
			temp=db.get(temp_key)
			if(temp.args):
				args=temp.args

		target_bbs=self.get_target_bbs(args);
		if(target_bbs):
			bbs_list=target_bbs

		template_values={
		'host':"./",
		'is_iphone':CssDesign.is_iphone(self),
		'is_tablet':CssDesign.is_tablet(self),
		'is_english':CssDesign.is_english(self),
		'temp_key':temp_key,
		'redirect_url':self.request.path+"?temp_key="+temp_key,
		'user':user,
		'bbs_list':bbs_list,
		'args':args,
		'user_name':user_name
		}
		render=template_select.render("/html/upload_temp.html", template_values)
		self.response.out.write(render)
