#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#スレッドにそれっぽい名前を付ける、20121001.htmlみたいな
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------


from google.appengine.ext import db
from google.appengine.api import memcache

import re
import random
import time

from myapp.UTC import UTC
from myapp.JST import JST

from myapp.Bbs import Bbs
from myapp.BbsConst import BbsConst
from myapp.MesThread import MesThread
from myapp.MappingId import MappingId
from myapp.MappingThreadIdUniqueCheck import MappingThreadIdUniqueCheck
from myapp.ApiObject import ApiObject

class MappingThreadId():
	@staticmethod
	def make_url(id_value,value):
		tmp=value.replace(tzinfo=UTC()).astimezone(JST())
		return "%d%d%d%d%d" %(tmp.year,tmp.month,tmp.day,tmp.second,id_value)

	@staticmethod
	def mapping(bbs,thread_key):
		#直値
		if(len(thread_key)>20):
			return ApiObject.get_cached_object(thread_key)
		
		#キャッシュヒット判定
		bbs_key=str(bbs.key())
		mapped_key=memcache.get(BbsConst.OBJECT_THREAD_ID_MAPPING_HEADER+"_"+bbs_key+"_"+thread_key)
		if mapped_key is not None:
			return ApiObject.get_cached_object(mapped_key)
		
		#探索
		query=db.Query(MesThread,keys_only=True)
		query.filter("bbs_key =",bbs)
		query.filter("short =",thread_key)
		thread=None
		try:
			thread=query[0]
			thread=ApiObject.get_cached_object(thread)
		except:
			thread=None

		#キャッシュに登録
		if thread and thread.short:
			new_key=str(thread.key())
			memcache.set(BbsConst.OBJECT_THREAD_ID_MAPPING_HEADER+"_"+bbs_key+"_"+thread.short,new_key,BbsConst.OBJECT_MAPPING_CACHE_TIME)
		
		#image_keyを取得しておく
		if thread and thread.image_key:
			thread.cached_image_key=str(thread.image_key.key())

		#スレッドを返す
		return thread
	
	@staticmethod
	def get_thread_url(host,bbs,thread):
		url=MappingId.get_usr_url(host,bbs)
		if(thread.short):
			url+=thread.short
		else:
			url+=str(thread.key())
		url+=".html"
		return url
	
	@staticmethod
	def assign(bbs,thread,exec_put):
		#既に短縮URLが割り当てられていればそのまま
		if(thread.short):
			return
		
		#ユニークIDをループしながら探索
		for id_value in range(1,9999):
			#URLを確定する
			new_url=MappingThreadId.make_url(id_value,thread.create_date)
			
			#排他制御込みで既に該当URLが作成されていないか確認する
			new_salt = str(time.time())+str(random.random())
			new_key_name="thread_short_"+str(bbs.key())+"_"+new_url
			unique_check=MappingThreadIdUniqueCheck.get_or_insert(key_name=new_key_name,salt=new_salt,bbs=bbs,thread=thread)
			
			#既に別のユーザが作成した
			if(unique_check.salt != new_salt):
				continue

			#作れたので更新
			thread.short=new_url
			if(exec_put):
				thread.put()
			break
		
