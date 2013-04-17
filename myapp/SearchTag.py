#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#タグを検索
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging
import urllib
import math

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.Counter import Counter
from myapp.Alert import Alert
from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8
from myapp.Entry import Entry
from myapp.OwnerCheck import OwnerCheck
from myapp.RecentCommentCache import RecentCommentCache
from myapp.CssDesign import CssDesign
from myapp.BbsConst import BbsConst
from myapp.MappingThreadId import MappingThreadId
from myapp.MesThread import MesThread
from myapp.RecentTag import RecentTag
from myapp.ApiObject import ApiObject
from myapp.OwnerCheck import OwnerCheck

class SearchTag(webapp.RequestHandler):
	@staticmethod
	def get_recent_tag(api):
		data=memcache.get(BbsConst.RECENT_TAG_CACHE_HEADER+api)
		if(not data):
			recent_tag=None
			try:
				recent_tag=RecentTag.get_by_key_name(BbsConst.RECENT_TAG_KEY_NAME)
			except:
				recent_tag=None
			if(recent_tag==None):
				return None
			return SearchTag.get_recent_tag_core(recent_tag,api)
		return data
	
	@staticmethod
	def get_recent_tag_core(recent_tag,api):
		tag_list=[]
		cnt=0
		for tag2 in recent_tag.tag_list:
			try:
				score=recent_tag.score_list[cnt]
			except:
				score="1"
			
			if(score=="0"):
				cnt=cnt+1
				continue
			
			one_tag='<a href="./'+api+'?tag='
			one_tag+=urllib.quote_plus(tag2.encode('utf8'))
			one_tag+='" class="decnone">'
			
			size=int(score)
			if(size>16):
				size=16
			size=round(math.log(size+1,2)+1)
			
			one_tag+='<font color="#258FB8" size="'+str(size)+'">'
			one_tag+=tag2+"("+str(score)+")"
			one_tag+='</font></a>'
			
			tag_list.append(one_tag)
			cnt=cnt+1
		
		memcache.set(BbsConst.RECENT_TAG_CACHE_HEADER+api,tag_list,BbsConst.RECENT_TAG_CACHE_TIME)
		
		return tag_list

	def get_thread(self,query,tag,thread_num,page):
		query.filter('tag_list =', tag)
		thread_key_list = query.fetch(limit=thread_num, offset=(page-1)*thread_num)
		#thread_list = ApiObject.get_cached_object_list(thread_key_list)
		thread_list = ApiObject.create_thread_object_list(self,thread_key_list,"search")
		return thread_list

	@staticmethod
	def update_recent_tag(tag,cnt,api):
		#最近のタグを取得
		recent_tag=RecentTag.get_or_insert(BbsConst.RECENT_TAG_KEY_NAME)
		
		#タグに対応するスレッドの数を更新
		if(not recent_tag.tag_list):
			recent_tag.tag_list=[]
		if(not recent_tag.score_list):
			recent_tag.score_list=[]
		try:
			search_index=recent_tag.tag_list.index(tag)
		except:
			search_index=-1

		if(search_index!=-1):
			recent_tag.tag_list.pop(search_index)
			if(len(recent_tag.score_list)>search_index):
				recent_tag.score_list.pop(search_index)

		if(cnt>0):
			recent_tag.tag_list.insert(0,tag)
			recent_tag.score_list.insert(0,str(cnt))
		
		cnt=len(recent_tag.tag_list)
		if(cnt>=100):
			recent_tag.tag_list.pop(cnt-1)
			recent_tag.score_list.pop(cnt-1)

		recent_tag.put()

		#最近のタグリストの構築
		tag_list=SearchTag.get_recent_tag_core(recent_tag,api)
		return tag_list

	def get(self):
		tag=self.request.get("tag")
		
		SetUtf8.set()

		#リダイレクト
		user=users.get_current_user()
		if(BbsConst.PINTEREST_MODE):
			if((user and OwnerCheck.is_admin(user)) or BbsConst.PINTEREST_MODE==2):
				self.redirect(str("./pinterest?tag="+urllib.quote_plus(str(tag))))
				return

		page=1
		thread_num=100

		#タグに対応するクエリを作成
		query = db.Query(MesThread,keys_only=True)
		query.filter('illust_mode =', BbsConst.ILLUSTMODE_ILLUST)
		query.order('-applause')
		thread_list = self.get_thread(query,tag,thread_num,page)

		query = db.Query(MesThread,keys_only=True)
		query.filter('illust_mode =', BbsConst.ILLUSTMODE_MOPER)
		query.order('-applause')
		moper_list = self.get_thread(query,tag,thread_num,page)
		
		query = db.Query(MesThread,keys_only=True)
		query.filter('illust_mode =', BbsConst.ILLUSTMODE_NONE)
		query.order('-date')
		text_list = self.get_thread(query,tag,thread_num,page)
		
		host_url="./";

		#最近のタグ
		cnt=len(thread_list)+len(moper_list)+len(text_list)
		tag_list=SearchTag.update_recent_tag(tag,cnt,"search_tag")

		#iPhoneかどうか
		is_iphone=CssDesign.is_iphone(self)
		
		#レンダリング
		template_values = {
			'host': host_url,
			'thread_list': thread_list,
			'moper_list': moper_list,
			'text_list': text_list,
			'tag': tag,
			'tag_list': tag_list,
			'is_iphone': is_iphone,
			'user': users.get_current_user(),
			'redirect_url': self.request.path,
			'mode': "bookmark"
		}

		path = os.path.join(os.path.dirname(__file__), "../html/portal.html")
		self.response.out.write(template.render(path, template_values))
