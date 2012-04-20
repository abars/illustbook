#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#タグで検索する

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

from Bbs import Bbs
from Counter import Counter
from Alert import Alert
from MappingId import MappingId
from SetUtf8 import SetUtf8
from Entry import Entry
from OwnerCheck import OwnerCheck
from RecentCommentCache import RecentCommentCache
from CssDesign import CssDesign
from BbsConst import BbsConst
from MappingThreadId import MappingThreadId
from MesThread import MesThread
from RecentTag import RecentTag

class SearchTag(webapp.RequestHandler):
	@staticmethod
	def get_recent_tag():
		data=memcache.get("recent_tag_list")
		if(not data):
			recent_tag=None
			try:
				recent_tag=RecentTag.get_by_key_name("recent_tag")
			except:
				recent_tag=None
			if(recent_tag==None):
				return None
			return SearchTag.get_recent_tag_core(recent_tag)
		return data
	
	@staticmethod
	def get_recent_tag_core(recent_tag):
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
			
			one_tag='<A HREF="./search_tag?tag='
			one_tag+=urllib.quote_plus(tag2.encode('utf8'))
			one_tag+='" class="decnone">'
			
			size=int(score)
			size=round(math.log(size+1,2)+1)
			
			one_tag+='<font color="#258FB8" SIZE='+str(size)+'>'
			one_tag+=tag2+"("+str(score)+")"
			one_tag+='</font></A>'
			
			tag_list.append(one_tag)
			cnt=cnt+1
		
		memcache.set("recent_tag_list",tag_list,60*60*24)
		
		return tag_list

	def get(self):
		tag=self.request.get("tag")
		
		SetUtf8.set()

		page=1
		thread_num=100

		query = MesThread.all()
		query.filter('tag_list =', tag)
		query.filter('illust_mode =', BbsConst.ILLUSTMODE_ILLUST)
		query.order('-applause')
		thread_list = query.fetch(limit=thread_num, offset=(page-1)*thread_num)

		query = MesThread.all()
		query.filter('tag_list =', tag)
		query.filter('illust_mode =', BbsConst.ILLUSTMODE_MOPER)
		query.order('-applause')
		moper_list = query.fetch(limit=thread_num, offset=(page-1)*thread_num)

		query = MesThread.all()
		query.filter('tag_list =', tag)
		query.filter('illust_mode =', BbsConst.ILLUSTMODE_NONE)
		query.order('-date')
		text_list = query.fetch(limit=thread_num, offset=(page-1)*thread_num)
		
		host_url="./";

		recent_tag=RecentTag.get_or_insert("recent_tag")
		
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

		cnt=len(thread_list)+len(moper_list)+len(text_list)
		if(cnt>0):
			recent_tag.tag_list.insert(0,tag)
			recent_tag.score_list.insert(0,str(cnt))
		
		cnt=len(recent_tag.tag_list)
		if(cnt>=100):
			recent_tag.tag_list.pop(cnt-1)
			recent_tag.score_list.pop(cnt-1)

		#最近のタグリストの構築
		tag_list=SearchTag.get_recent_tag_core(recent_tag)

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
			'redirect_url': self.request.path
		}

		path = os.path.join(os.path.dirname(__file__), "html/portal/general_show_bookmark.html")
		self.response.out.write(template.render(path, template_values))

		recent_tag.put()
