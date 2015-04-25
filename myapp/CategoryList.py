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

import template_select
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
		return CategoryList._get_category_dic(bbs,None)

	@staticmethod
	def _get_category_dic(bbs,new_category):
		#文字列->リスト
		category_list=[]
		if(bbs.category_list and bbs.category_list!=""):
			category_list=bbs.category_list.split(",")
		else:
			bbs.category_list=""
		
		#カテゴリとカウントの分離
		dic=[]
		category_found=False
		updated=False
		for text in category_list:
			m = re.search('(.*)\(([0-9]*)\)', text)
			if m:
				name=m.group(1)
				count=m.group(2)
			else:
				name=text
				count=-1
			if(name==""):
				continue

			#カテゴリの更新を行う場合
			if(new_category):
				if(name==new_category):
					count=-1
					category_found=True

			#更新リクエスト
			if(count==-1):
				count=MesThread.all().filter("bbs_key =",bbs).filter("category =",name).count(limit=1000)
				updated=True
				if(bbs.disable_category_sort):
					dic.append({"category":name,"count":count})
				else:
					dic.insert(0,{"category":name,"count":count})
			else:
				dic.append({"category":name,"count":count})
		
		#カテゴリが存在しなかったら新規追加
		if(new_category and (not category_found)):
			dic.insert(0,{"category":new_category,"count":1})
			updated=True

		#更新
		if(updated):
			CategoryList._put_category_dic(bbs,dic)
		
		return dic
	
	@staticmethod
	def _put_category_dic(bbs,category_dic):
		category_list_text=""
		for one in category_dic:
			category=one["category"]
			count=one["count"]
			if(len(category)==0):
				next
			category_list_text=category_list_text+category+"("+str(count)+"),"
		bbs.category_list=category_list_text
		bbs.put()

	@staticmethod
	def add_new_category(bbs,category):
		#update request
		category_dic=CategoryList._get_category_dic(bbs,category)
