#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#更新情報系の公開API
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import logging

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api.users import User

import template_select

from myapp.SetUtf8 import SetUtf8
from myapp.Alert import Alert
from myapp.MesThread import MesThread
from myapp.MappingId import MappingId
from myapp.Bbs import Bbs
from myapp.BbsConst import BbsConst
from myapp.Bookmark import Bookmark
from myapp.AddBookmark import AddBookmark
from myapp.ApiObject import ApiObject
from myapp.Ranking import Ranking
from myapp.EventList import EventList
from myapp.SearchThread import SearchThread

class ApiFeed(webapp.RequestHandler):

#-------------------------------------------------------------------
#feed class
#-------------------------------------------------------------------

	@staticmethod
	def invalidate_cache():
		offset=BbsConst.PINTEREST_CACHE_OFFSET #0
		mode=BbsConst.PINTEREST_CACHE_MDOE #["bookmark","new","moper","hot","applause"]
		count=[BbsConst.PINTEREST_PAGE_UNIT] #[16,18,BbsConst.PINTEREST_PAGE_UNIT]
		for o in offset:
			for m in mode:
				for c in count:
					memcache.delete(ApiFeed._get_cache_id(m,None,o,c))
	
	@staticmethod
	def _get_cache_id(order,bbs_id,offset,limit):
		if(not order):
			order="none"
		if(not bbs_id):
			bbs_id="none"
		return BbsConst.OBJECT_CACHE_HEADER+"_"+order+"_"+bbs_id+"_"+str(offset)+"_"+str(limit)
	
	@staticmethod
	def _get_query(order,event_id):
		query=db.Query(MesThread,keys_only=True)
		if(order=="bookmark"):
			query.order("-bookmark_count")
			query.filter("illust_mode =",BbsConst.ILLUSTMODE_ILLUST)
		if(order=="new"):
			query.order("-create_date")
			query.filter("illust_mode =",BbsConst.ILLUSTMODE_ILLUST)
		if(order=="applause"):
			query.order("-applause")
			query.filter("illust_mode =",BbsConst.ILLUSTMODE_ILLUST)
		if(order=="moper"):
			query.order("-create_date")
			query.filter("illust_mode =",BbsConst.ILLUSTMODE_MOPER)
		if(order=="2010" or order=="2011" or order=="2012" or order=="2013"):
			date=datetime.date(int(order)+1,1,1)
			query.order("-create_date")
			query.filter("create_date <",date)
			query.filter("illust_mode =",BbsConst.ILLUSTMODE_ILLUST)
		if(order=="event"):
			if(not event_id):
				event_list=EventList.get_event_list()
				if(event_list):
					event_id=event_list[0].id
				else:
					event_id="no_event_opened"
				query.order("-create_date")
			else:
				query.order("-applause")
			query.filter("illust_mode =",BbsConst.ILLUSTMODE_ILLUST)
			query.filter("event_id =",event_id)
		if(not order):
			query.order("-create_date")
			query.filter("illust_mode =",BbsConst.ILLUSTMODE_ILLUST)
		return query
		
	@staticmethod
	def feed_get_ranking_thread_list(month_query,page,unit):
		#日付の範囲を決定
		if(month_query==""):
			from_month=datetime.date.today()+datetime.timedelta(days=-30)
			next_month=datetime.date.today()
			no_reduct=False
		else:
			today=datetime.datetime.strptime(month_query,"%Y-%m-%d")
			from_month=datetime.datetime(today.year,today.month,today.day).strftime('%Y-%m-%d')
			if(today.month==12):
				next_month=datetime.datetime(today.year+1,1,today.day).strftime('%Y-%m-%d')
			else:
				next_month=datetime.datetime(today.year,today.month+1,today.day).strftime('%Y-%m-%d')
			no_reduct=True

		#キャッシュ取得
		order="monthly"
		offset=(page-1)*unit
		if(month_query==""):
			cache_enable=ApiFeed._is_cache_enable(offset,unit,order)
		else:
			cache_enable=False
		cache_id=ApiFeed._get_cache_id(order,None,offset,unit)
		if(cache_enable):
			data=memcache.get(cache_id)
			if(data):
				return data

		#検索範囲を絞らなければ正常にソートできないので、できるだけ絞る
		search_str="(bookmark >= 1 OR applause >= 3) AND date > "+str(from_month)+" AND date < "+str(next_month)
		thread_list=SearchThread.search(search_str,page,unit,BbsConst.SEARCH_THREAD_INDEX_NAME,no_reduct)

		#キャッシュに乗せる
		if(cache_enable):
			memcache.set(cache_id,thread_list,BbsConst.TOPPAGE_FEED_CACHE_TIME)

		return thread_list

	@staticmethod
	def _is_cache_enable(offset,limit,order):
		#キャッシュの有効フラグ
		cache_enable=0
		if(offset in BbsConst.PINTEREST_CACHE_OFFSET):#==0):
			if(limit==BbsConst.PINTEREST_PAGE_UNIT):
				cache_enable=1

		#更新されたときにページ間で不整合が発生するために無効化
		if(order):
			if(not(order in BbsConst.PINTEREST_CACHE_MDOE)):
				cache_enable=0

		return cache_enable

	@staticmethod
	def feed_get_thread_list(req,order,offset,limit):
		#最大取得数
		if(limit>100):
			limit=100

		#キャッシュが有効かどうか
		cache_enable=ApiFeed._is_cache_enable(offset,limit,order)

		#キャッシュ取得
		cache_id=ApiFeed._get_cache_id(order,req.request.get("bbs_id"),offset,limit)
		if(cache_enable):
			data=memcache.get(cache_id)
			if(data):
				dic=ApiObject.create_thread_object_list(req,data,req.request.get("bbs_id"))
				return dic
		
		#スレッド一覧取得
		if(order=="hot"):
			rank=Ranking.get_by_key_name(BbsConst.THREAD_RANKING_KEY_NAME)
			if(rank==None):
				rank=Ranking.get_or_insert(BbsConst.THREAD_RANKING_KEY_NAME)
			thread_list=rank.get_rank(offset,limit)
			bbs_id=None
		else:
			query=ApiFeed._get_query(order,req.request.get("event_id"))

			bbs_id=None
			if(req.request.get("bbs_id")):
				bbs_key=MappingId.mapping(req.request.get("bbs_id"))
				if(bbs_key==""):
					return None #bbs not found
				query.filter("bbs_key =",db.get(bbs_key))
				bbs_id=True

			thread_list=query.fetch(offset=offset,limit=limit)
		
		#キャッシュに乗せる
		if(cache_enable):
			memcache.set(cache_id,thread_list,BbsConst.TOPPAGE_FEED_CACHE_TIME)

		#リスト作成
		dic=ApiObject.create_thread_object_list(req,thread_list,bbs_id)

		return dic

	@staticmethod
	def feed_get_bbs_list(req,order,offset,limit):
		#最大取得数
		if(limit>100):
			limit=100

		#キャッシュが有効かどうか
		cache_enable=0
		if(offset==0):
			cache_enable=1
		
		#キャッシュ取得
		cache_id=BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_BBS_RANKING_HEADER
		if(cache_enable):
			data=memcache.get(cache_id)
		else:
			data=None
		if(data and cache_enable):
			return data
		
		#BBS一覧取得
		rank=Ranking.get_by_key_name(BbsConst.THREAD_RANKING_KEY_NAME)
		if(rank==None):
			rank=Ranking.get_or_insert(BbsConst.THREAD_RANKING_KEY_NAME)
		bbs_list=rank.get_bbs_rank(offset,limit)
		
		#リスト作成
		dic=[]
		bbs_list=ApiObject.get_cached_object_list(bbs_list)
		for bbs in bbs_list:
			dic.append(ApiObject.create_bbs_object(req,bbs))

		#キャッシュに乗せる
		if(cache_enable):
			memcache.set(cache_id,dic,BbsConst.TOPPAGE_FEED_CACHE_TIME)
		
		return dic

#-------------------------------------------------------------------
#main
#-------------------------------------------------------------------

	def get(self):
		SetUtf8.set()
		if(ApiObject.check_api_capacity(self)):
			return
		dic=ApiFeed.get_core(self)
		ApiObject.write_json_core(self,dic)

	@staticmethod
	def get_core(self):
		#パラメータ取得
		method=""
		if(self.request.get("method")):
			method=self.request.get("method");
		
		user_id=""
		if(self.request.get("user_id")):
			user_id=self.request.get("user_id")
		
		#返り値
		dic={"method":method}

		#フィードクラス
		if(method=="getThreadList"):
			offset=0
			if(self.request.get("offset")):
				try:
					offset=int(self.request.get("offset"))
				except:
					return {"status":"failed","message":"offset must be integer"}
			limit=10
			if(self.request.get("limit")):
				try:
					limit=int(self.request.get("limit"))
				except:
					return {"status":"failed","message":"limit must be integer"}
			order=self.request.get("order")
			dic=ApiFeed.feed_get_thread_list(self,order,offset,limit)
			if(dic==None):
				return {"status":"failed","message":"bbs not found"}
			#return {"status":"failed","message":"debug error message"}

		dic=ApiObject.add_json_success_header(dic)
		return dic
		

