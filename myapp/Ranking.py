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

from google.appengine.ext import db
from google.appengine.api.labs import taskqueue

from myapp.BbsConst import BbsConst
from myapp.ApiObject import ApiObject
from myapp.MesThread import MesThread

class Ranking(db.Model):
	#カウンターの加算時と、拍手時、ブックマーク時にスレッドとユーザを追加する
	thread_list = db.ListProperty(db.Key,indexed=False)
	user_list = db.StringListProperty(indexed=False)
	
	#イラストのランキング結果と、ユーザのランキング結果を格納
	#ランキングの更新はcronで行う
	ranking_list = db.ListProperty(db.Key,indexed=False)
	bbs_ranking_list = db.StringListProperty(indexed=False)
	user_id_ranking_list = db.StringListProperty(indexed=False)

	#以下のランキングは廃止
	user_ranking_list = db.StringListProperty(indexed=False)
	owner_list = db.StringListProperty(indexed=False)
	owner_ranking_list = db.StringListProperty(indexed=False)
	owner_id_ranking_list = db.StringListProperty(indexed=False)

	date = db.DateTimeProperty(auto_now=True,indexed=False)
	
	def reset(self):
		self.thread_list=[]
	
	def _add_rank_core(self,key,key_list,n):
		if(not key):
			return
		content_len=len(key_list)
		while(content_len>=n):
			key_list.pop(0)
			content_len=content_len-1
		key_list.append(key)
	
	@staticmethod
	def add_rank_global(thread,score):	
		if(thread.illust_mode==BbsConst.ILLUSTMODE_ILLUST):
			headers={'X-AppEngine-FailFast' : 'true'} #新規インスタンスの作成の抑制
			try:
				taskqueue.add(url="/add_ranking_score",params={"thread":str(thread.key()),"user_id":str(thread.user_id),"score":score},queue_name="score",headers=headers)
			except:
				logging.warning("ranking score taskqueue add failed")

	def add_rank_from_taskqueue(self,thread_key,user_id,score):
		for cnt in range(score):
			self._add_rank_core(thread_key,self.thread_list,BbsConst.THREAD_RANKING_RECENT)
			#self._add_rank_core(user_id,self.user_list,BbsConst.USER_RANKING_RECENT)
			self.user_list=[]	#deleted
		self.put()

	def get_sec(self,now):
		return int(time.mktime(now.timetuple()))

	def create_rank(self,req):
		self._create_ranking_core()
		
		#削除した要素
		self.user_ranking_list=["empty"]
		self.owner_list = ["empty"]
		self.owner_ranking_list = ["empty"]
		self.owner_id_ranking_list = ["empty"]
		
		self.put()
	
	def _create_ranking_core(self):
		#ハッシュにthread_keyを入れていく
		rank={}
		for thread in self.thread_list:
			if(rank.has_key(thread)):
				rank[thread]=rank[thread]+1
			else:
				rank[thread]=1
		
		#1次ランキングを作成
		#（全てでthreadの実体を取得すると重いので）
		first_ranking_list=[]
		for k, v in sorted(rank.items(), key=lambda x:x[1], reverse=True):
			if(v>=1):
				first_ranking_list.append(k)
				if(len(first_ranking_list)>=BbsConst.THREAD_RANKING_MAX*BbsConst.THREAD_RANKING_BEFORE_FILTER_MULT):
					break
		
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
			
			#経過日数で補正
			day_left=(self.get_sec(datetime.datetime.now())-self.get_sec(thread.create_date))/60/60/24
			day_left=day_left/7+1	#1週間で1/2
			#rank[k]=rank[k]/day_left
			#if(rank[k]<1):
			#	rank[k]=1
		
			#BBSランクを加算
			if(thread):
				bbs=thread.cached_bbs_key
				bbs_main=ApiObject.get_cached_object(bbs)
				if(not(bbs_main and bbs_main.disable_news)):
					if(not rank_bbs.has_key(bbs)):
						rank_bbs[bbs]=0
					rank_bbs[bbs]=rank_bbs[bbs]+rank[k]

			#USERランクを加算
			if(thread):
				user_id=thread.user_id
				if(user_id):
					if(not rank_user.has_key(user_id)):
						rank_user[user_id]=0
					rank_user[user_id]=rank_user[user_id]+rank[k]
			
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

