#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#�X���b�h�ɂ�����ۂ����O��t����A20121001.html�݂�����
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
		#���l
		if(len(thread_key)>20):
			return ApiObject.get_cached_object(thread_key)#db.get(thread_key)
		
		#�L���b�V���q�b�g����
		bbs_key=str(bbs.key())
		mapped_key=memcache.get(BbsConst.OBJECT_THREAD_ID_MAPPING_HEADER+"_"+bbs_key+"_"+thread_key)
		if mapped_key is not None:
			return ApiObject.get_cached_object(mapped_key)
		
		#�T��
		query=MesThread.all()
		query.filter("bbs_key =",bbs)
		query.filter("short =",thread_key)
		thread=None
		try:
			thread=query[0]
		except:
			thread=None
		
		#�L���b�V���ɓo�^
		if thread and thread.short:
			new_key=str(thread.key())
			memcache.set(BbsConst.OBJECT_THREAD_ID_MAPPING_HEADER+"_"+bbs_key+"_"+thread.short,new_key,BbsConst.OBJECT_MAPPING_CACHE_TIME)
		
		#image_key���擾���Ă���
		if thread and thread.image_key:
			thread.cached_image_key=str(thread.image_key.key())

		#�X���b�h��Ԃ�
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
		#���ɒZ�kURL�����蓖�Ă��Ă���΂��̂܂�
		if(thread.short):
			return
		
		#���j�[�NID�����[�v���Ȃ���T��
		for id_value in range(1,9999):
			#URL���m�肷��
			new_url=MappingThreadId.make_url(id_value,thread.create_date)
			
			#�r�����䍞�݂Ŋ��ɊY��URL���쐬����Ă��Ȃ����m�F����
			new_salt = str(time.time())+str(random.random())
			new_key_name="thread_short_"+str(bbs.key())+"_"+new_url
			unique_check=MappingThreadIdUniqueCheck.get_or_insert(key_name=new_key_name,salt=new_salt,bbs=bbs,thread=thread)
			
			#���ɕʂ̃��[�U���쐬����
			if(unique_check.salt != new_salt):
				continue

			#��ꂽ�̂ōX�V
			thread.short=new_url
			if(exec_put):
				thread.put()
			break
		
