#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ランキング
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import datetime;
import time;

from google.appengine.ext import db

from myapp.BbsConst import BbsConst
from myapp.ApiObject import ApiObject

class Ranking(db.Model):
	thread_list = db.ListProperty(db.Key)
	user_list = db.StringListProperty()
	owner_list = db.StringListProperty()
	
	ranking_list = db.ListProperty(db.Key)
	owner_ranking_list = db.StringListProperty()
	user_ranking_list = db.StringListProperty()

	date = db.DateTimeProperty(auto_now=True)
	
	def reset(self):
		self.thread_list=[]
	
	def _add_rank_core(self,key,key_list):
		if(not key):
			return
		n=2500
		content_len=len(key_list)
		while(content_len>=n):
			key_list.pop(0)
			content_len=content_len-1
		key_list.append(key)
	
	def add_rank(self,thread):
		if(not self.thread_list):
			self.thread_list=[]
		self._add_rank_core(thread.key(),self.thread_list)
		self._add_rank_core(thread.bbs_key.user_id,self.owner_list)
		self._add_rank_core(thread.user_id,self.user_list)
		self.put()

	def get_sec(self,now):
		return int(time.mktime(now.timetuple()))

	def create_rank(self):
		self.create_thread_rank()
		self.create_user_rank()
		self.put()
	
	def create_user_rank(self):
		rank_user={}
		rank_owner={}
		
		for user_id in self.user_list:
			if(user_id):
				if(rank_user.has_key(user_id)):
					rank_user[user_id]=rank_user[user_id]+1
				else:
					rank_user[user_id]=1

		for user_id in self.owner_list:
			if(user_id):
				if(rank_owner.has_key(user_id)):
					rank_owner[user_id]=rank_owner[user_id]+1
				else:
					rank_owner[user_id]=1
		
		cnt=0
		self.owner_ranking_list=[]
		for k, v in sorted(rank_owner.items(), key=lambda x:x[1], reverse=True):
			if(v>=1):
				self.owner_ranking_list.append(k)
				cnt=cnt+1
				if(cnt>=BbsConst.THREAD_RANKING_MAX):
					break

		cnt=0
		self.user_ranking_list=[]
		for k, v in sorted(rank_user.items(), key=lambda x:x[1], reverse=True):
			if(v>=1):
				self.user_ranking_list.append(k)
				cnt=cnt+1
				if(cnt>=BbsConst.THREAD_RANKING_MAX):
					break
	
	def create_thread_rank(self):
		#ハッシュにthread_keyを入れていく
		rank={}
		for thread in self.thread_list:
			if(rank.has_key(thread)):
				rank[thread]=rank[thread]+1
			else:
				rank[thread]=1
		
		#スコア補正
		for k,v in rank.items():
			#存在しているものだけ
			thread=ApiObject.get_cached_object(k)
			
			#イラストモードだけ
			if(not thread or thread.illust_mode!=BbsConst.ILLUSTMODE_ILLUST):
				rank[k]=0
				continue
			
			#経過日数
			day_left=(self.get_sec(datetime.datetime.now())-self.get_sec(thread.create_date))/60/60/24
			day_left=day_left/7+1	#1週間で1/2
			
			#拍手とブックマークスコアを加算
			if(thread.applause):
				rank[k]=rank[k]+thread.applause/day_left
			if(thread.bookmark_count):
				rank[k]=rank[k]+thread.bookmark_count/day_left
		
		#ランキング作成
		cnt=0
		self.ranking_list=[]
		for k, v in sorted(rank.items(), key=lambda x:x[1], reverse=True):
			if(v>=1):
				self.ranking_list.append(k)
				cnt=cnt+1
				if(cnt>=BbsConst.THREAD_RANKING_MAX):
					break
		
	def get_rank(self,offset,limit):
		if(not self.ranking_list):
			return []
		return self.ranking_list[offset:offset+limit]
	
	def get_rank_core(self,user_id,list):
		cnt=1
		for i in list:
			if(i==user_id):
				return cnt
			cnt=cnt+1
		return 0
	
	def get_user_rank(self,user_id):
		return self.get_rank_core(user_id,self.user_ranking_list)

	def get_owner_rank(self,user_id):
		return self.get_rank_core(user_id,self.owner_ranking_list)
		
