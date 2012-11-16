#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#カテゴリを追加する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging
import base64
import re

from collections import OrderedDict

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.MesThread import MesThread
from myapp.BbsConst import BbsConst

class CategoryList(webapp.RequestHandler):
	@staticmethod
	def get_category_list(bbs):
		dic=CategoryList.get_category_dic(bbs)
		ret=[]
		for text in dic.keys():
			ret.append({"category":text,"count":dic[text]})
		return ret

	@staticmethod
	def get_category_dic(bbs):
		#文字列->リスト
		category_list=[]
		if(bbs.category_list and bbs.category_list!=""):
			category_list=bbs.category_list.split(",")
		else:
			bbs.category_list=""
		
		#カウント分離
		dic=OrderedDict()
		for text in category_list:
			m = re.search('(.*)\(([0-9]*)\)', text)
			if m:
				name=m.group(1)
				count=m.group(2)
			else:
				name=text
				count=-1
			dic[name]=count
		
		#カウント値更新
		updated=False
		for category in dic.keys():
			if(dic[category]==-1):
				dic[category]=MesThread.all().filter("bbs_key =",bbs).filter("category =",category).count(limit=100)
				updated=True
		if(updated):
			CategoryList.put_category_dic(bbs,dic)
		
		return dic
	
	@staticmethod
	def put_category_dic(bbs,category_dic):
		category_list_text=""
		for category in category_dic.keys():
			if(len(category)==0):
				next
			if(category_dic[category]==-1):
				category_list_text=category_list_text+category+","
			else:
				category_list_text=category_list_text+category+"("+str(category_dic[category])+"),"
		bbs.category_list=category_list_text
		bbs.put()

	@staticmethod
	def add_new_category(bbs,category):
		category_dic=CategoryList.get_category_dic(bbs)
		if not (category in category_dic.keys()):
			category_dic[category]=-1	#カテゴリを追加
		category_dic[category]=-1	#カウント更新リクエスト
		CategoryList.put_category_dic(bbs,category_dic)
