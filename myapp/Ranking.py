#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ランキング
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import datetime;
import time;
import json;
import logging;
import os;

from google.appengine.ext import db
from google.appengine.api.labs import taskqueue

from myapp.BbsConst import BbsConst
from myapp.ApiObject import ApiObject
from myapp.MesThread import MesThread
from myapp.AnalyticsGet import AnalyticsGet
from myapp.MappingId import MappingId
from myapp.MappingThreadId import MappingThreadId
from myapp.SearchThread import SearchThread
from myapp.RecentTag import RecentTag
from google.appengine.api import memcache

class Ranking(db.Model):
	#イラストのランキング結果と、ユーザのランキング結果を格納
	#ランキングの更新はcronで行う
	ranking_list = db.ListProperty(db.Key,indexed=False)
	bbs_ranking_list = db.StringListProperty(indexed=False)
	user_id_ranking_list = db.StringListProperty(indexed=False)

	date = db.DateTimeProperty(auto_now=True,indexed=False)
	
	def reset(self):
		self.ranking_list=[]
	
	@staticmethod
	def add_rank_global(thread,score):
		#Analytics APIを使ってランキングを作成するようになったので不要になった
		return

	def add_rank_from_taskqueue(self,thread_key,user_id,score):
		#Analytics APIを使ってランキングを作成するようになったので不要になった
		return

	def get_sec(self,now):
		return int(time.mktime(now.timetuple()))

	def get_tag_list(self,analytics):
		start_date=str(datetime.date.today()+datetime.timedelta(days=-7))
		end_date=str(datetime.date.today())
		result=analytics.get("tag","",start_date,end_date)

		recent_tag=RecentTag.get_or_insert(BbsConst.RECENT_TAG_KEY_NAME)
		recent_tag.tag_list=[]
		recent_tag.score_list=[]
		
		for one in result:
			url=one["ga:pagePath"]
			data=url.split("=")
			count=int(one["ga:pageviews"])
			query=data[1]
			
			search_found=SearchThread.get_count(query)

			recent_tag.tag_list.append(query)
			recent_tag.score_list.append(str(search_found))

		recent_tag.put()
		memcache.delete(BbsConst.RECENT_TAG_CACHE_HEADER)

	def get_thread_list(self,analytics):
		start_date=str(datetime.date.today()+datetime.timedelta(days=-1))
		end_date=str(datetime.date.today())
		result=analytics.get("page",".*",start_date,end_date)

		thread_list=[]
		for one in result:
			url=one["ga:pagePath"]
			count=int(one["ga:pageviews"])

			data=url.split("/")
			try:
				bbs_name=str(data[1])
				thread_name=str(data[2].split(".")[0])
			except:
				continue

			bbs_key=MappingId.mapping(bbs_name)
			bbs=ApiObject.get_cached_object(bbs_key)
			if(not bbs):
				continue
			thread = MappingThreadId.mapping(bbs,thread_name)
			if(not thread):
				continue

			while(count>=1):
				thread_list.append(thread.key())
				count=count-1

		return thread_list

	def create_rank(self,req):
		#analytics apiから生成

		analytics=AnalyticsGet()
		analytics.create_session()

		tag_list=self.get_tag_list(analytics)
		
		thread_list=self.get_thread_list(analytics)
		if os.environ["SERVER_SOFTWARE"].find("Development")!=-1:
			thread_list=db.Query(MesThread,keys_only=True).order("-create_date").fetch(limit=100)
		self._create_ranking_core(thread_list)

		self.put()
	
	def _create_ranking_core(self,thread_list):
		#ハッシュにthread_keyを入れていく
		rank={}
		first_ranking_list=[]
		for thread in thread_list:
			if(rank.has_key(thread)):
				rank[thread]=rank[thread]+1
			else:
				rank[thread]=1
				first_ranking_list.append(thread)

		#1次ランキングに出現したもののスコア補正
		rank_bbs={}
		rank_user={}
		for k in first_ranking_list:
			#スレッドの実体を取得
			thread=ApiObject.get_cached_object(k)

			#イラストモードだけ
			if(not thread or thread.illust_mode!=BbsConst.ILLUSTMODE_ILLUST):
				rank[k]=0
				continue
			
			#BBSランクを加算(純粋PV)
			if(thread):
				bbs=thread.cached_bbs_key
				bbs_main=ApiObject.get_cached_object(bbs)
				if(not(bbs_main and bbs_main.disable_news)):
					if(not rank_bbs.has_key(bbs)):
						rank_bbs[bbs]=0
					rank_bbs[bbs]=rank_bbs[bbs]+rank[k]

			#USERランクを加算(純粋PV)
			if(thread):
				user_id=thread.user_id
				if(user_id):
					if(not rank_user.has_key(user_id)):
						rank_user[user_id]=0
					rank_user[user_id]=rank_user[user_id]+rank[k]

			#経過日数と付加情報で補正
			day_left=(self.get_sec(datetime.datetime.now())-self.get_sec(thread.create_date))*1.0/60/60/24
			score=0
			if(thread.bookmark_count):
				score=score+thread.bookmark_count*5
			if(thread.applause):
				score=score+thread.applause
			rank[k]=(rank[k]+score)/(day_left+1)

			#非表示スレッドのランクを落とす
			if(thread and bbs_main and bbs_main.disable_news):
				rank[k]=0
			
		#スレッドランキング作成
		self.ranking_list=[]
		for k, v in sorted(rank.items(), key=lambda x:x[1], reverse=True):
			self.ranking_list.append(k)
			if(len(self.ranking_list)>=BbsConst.THREAD_RANKING_MAX):
				break

		#BBSランキング作成
		self.bbs_ranking_list=[]
		for k, v in sorted(rank_bbs.items(), key=lambda x:x[1], reverse=True):
			self.bbs_ranking_list.append(k)
			if(len(self.bbs_ranking_list)>=BbsConst.BBS_RANKING_MAX):
				break

		#USERランキング作成
		self.user_id_ranking_list=[]
		for k, v in sorted(rank_user.items(), key=lambda x:x[1], reverse=True):
			self.user_id_ranking_list.append(k)
			if(len(self.user_id_ranking_list)>=BbsConst.USER_RANKING_MAX):
				break
		
	def get_rank(self,offset,limit):
		if(not self.ranking_list):
			return []
		return self.ranking_list[offset:offset+limit]

	def get_bbs_rank(self,offset,limit):
		if(not self.bbs_ranking_list):
			return []
		return self.bbs_ranking_list[offset:offset+limit]
	
	def _get_rank_core(self,user_id,list):
		try:
			return list.index(user_id)+1
		except:
			return 0
	
	def get_user_rank(self,user_id):
		return self._get_rank_core(user_id,self.user_id_ranking_list)

