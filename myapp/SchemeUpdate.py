#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
# DataStoreのスキーマを変更する
# HRDの移植用だったのでもういらない
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

webapp.template.register_template_library('templatetags.django_filter')

from MesThread import MesThread
from ThreadImage import ThreadImage
from BbsConst import BbsConst
from Bookmark import Bookmark
from Entry import Entry

#-----------------------------------------------------------------
#オーナー情報更新
#-----------------------------------------------------------------

class SchemeUpdate(webapp.RequestHandler):
	def get(self):
		#SchemeUpdate.update_thread(self)
		#SchemeUpdate.update_moper(self)
		#SchemeUpdate.update_bookmark(self)
		#SchemeUpdate.update_entry(self)
		return
	
	@staticmethod
	def update_thread(main):
		query=MesThread.all()
		
		total_cnt=0
		update_cnt=0
		
		offset=0
		if(main.request.get("from")):
			offset=int(main.request.get("from"))
			
		offset_to=10000
		if(main.request.get("to")):
			offset_to=int(main.request.get("to"))

		while(offset<offset_to):
			list=query.fetch(limit=1000,offset=offset)
			for thread in list:
				total_cnt=total_cnt+1
				if(not thread.image_key and thread.image):
					thread.image_key=db.get(thread.image)
					thread.put()
					update_cnt=update_cnt+1
					if(update_cnt>=500):
						break
			offset=offset+1000
			if(update_cnt>=500):
				break
		
		main.response.out.write("total"+str(total_cnt)+" update"+str(update_cnt))

	@staticmethod
	def update_entry(main):
		query=Entry.all()
		query.filter("illust_reply =",1)
		
		total_cnt=0
		update_cnt=0
		
		offset=0
		if(main.request.get("from")):
			offset=int(main.request.get("from"))
			
		offset_to=10000
		if(main.request.get("to")):
			offset_to=int(main.request.get("to"))

		while(offset<offset_to):
			list=query.fetch(limit=1000,offset=offset)
			for entry in list:
				total_cnt=total_cnt+1
				if(entry.illust_reply_image_key):#not entry.illust_reply_image_key and entry.illust_reply_image):
					#entry.illust_reply_image_key=db.get(entry.illust_reply_image)
					entry.date=entry.create_date
					entry.put()
					update_cnt=update_cnt+1
					if(update_cnt>=500):
						break
			offset=offset+1000
			if(update_cnt>=500):
				break
		
		main.response.out.write("total"+str(total_cnt)+" update"+str(update_cnt))

	@staticmethod
	def update_moper(main):
		query=ThreadImage.all()
		query.filter("illust_mode =",BbsConst.ILLUSTMODE_MOPER)
		
		total_cnt=0
		update_cnt=0
		
		offset=0
		if(main.request.get("from")):
			offset=int(main.request.get("from"))
			
		offset_to=10000
		if(main.request.get("to")):
			offset_to=int(main.request.get("to"))

		while(offset<offset_to):
			list=query.fetch(limit=1000,offset=offset)
			for thread in list:
				total_cnt=total_cnt+1
				if(not thread.chunk_list_key and thread.chunk_list):
					thread.chunk_list_key=[]
					for chunk in thread.chunk_list:
						thread.chunk_list_key.append(db.Key(chunk))
					thread.put()
					update_cnt=update_cnt+1
					if(update_cnt>=500):
						break
			offset=offset+1000
			if(update_cnt>=500):
				break
		
		main.response.out.write("total"+str(total_cnt)+" update"+str(update_cnt))

	@staticmethod
	def update_bookmark(main):
		query=Bookmark.all()
		
		total_cnt=0
		update_cnt=0
		
		offset=0
		if(main.request.get("from")):
			offset=int(main.request.get("from"))
			
		offset_to=10000
		if(main.request.get("to")):
			offset_to=int(main.request.get("to"))

		while(offset<offset_to):
			list=query.fetch(limit=1000,offset=offset)
			for bookmark in list:
				total_cnt=total_cnt+1
				
				update_require=0

				if(not bookmark.thread_key_list and bookmark.thread_list):
					bookmark.thread_key_list=[]
					for thread in bookmark.thread_list:
						bookmark.thread_key_list.append(db.Key(thread))
					update_require=1

				if(not bookmark.bbs_key_list and bookmark.bbs_list):
					bookmark.bbs_key_list=[]
					for bbs in bookmark.bbs_list:
						bookmark.bbs_key_list.append(db.Key(bbs))
					update_require=1
				
				if(update_require):
					bookmark.put()
					update_cnt=update_cnt+1
					if(update_cnt>=500):
						break
			offset=offset+1000
			if(update_cnt>=500):
				break
		
		main.response.out.write("total"+str(total_cnt)+" update"+str(update_cnt))
		
	
