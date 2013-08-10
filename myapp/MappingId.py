#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#http://www.illustbook.net/[ID]/の[ID]からkeyにマップする
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import memcache

import re

from myapp.Bbs import Bbs
from myapp.BbsConst import BbsConst

class MappingId():
	@staticmethod
	def check_capability(check_id,bbs_key):
		if(check_id==""):
			return 1
		if(check_id=="usr"):
			return 0
		if(check_id=="img"):
			return 0
		if(check_id=="js"):
			return 0
		if(check_id=="bin"):
			return 0
		if(check_id=="swf"):
			return 0
		if(check_id=="code"):
			return 0
		if(check_id=="flash"):
			return 0
		if(check_id=="static_files"):
			return 0
		if(check_id=="static_files_stable"):
			return 0
		if(check_id=="twitter"):
			return 0
		if(check_id=="css"):
			return 0
		if(check_id=="app"):
			return 0
		if(check_id=="thumbnail"):
			return 0
		if(check_id=="template"):
			return 0
		if(check_id=="tolot"):
			return 0
		query=Bbs.all()
		query.filter("short =",check_id)
		cnt=query.count()
		if(cnt==0):
			return 1
		if(bbs_key!=""):
			if(str(query[0].key())==bbs_key):
				return 1
		return 0
	
	@staticmethod
	def key_format_check(key):
		if(key==""):
			return 0
		regexp = re.compile(r'^[0-9A-Za-z_]+$')
		result = regexp.search(key)
		if result != None :
			return 0
		return 1  	
	
	@staticmethod
	def mapping(bbs_key):
		#直値
		if(len(bbs_key)>16):
			return bbs_key

		#キャッシュヒット判定
		data=memcache.get(BbsConst.OBJECT_BBS_ID_MAPPING_HEADER+bbs_key)
		if data is not None:
			return data

		#BBSのIDに対応するBBSを取得
		query=Bbs.all()
		query.filter("short =",bbs_key)
		try:
			data=str(query[0].key())
		except:
			return ""
		
		#キーを返す
		memcache.set(BbsConst.OBJECT_BBS_ID_MAPPING_HEADER+bbs_key,data,BbsConst.OBJECT_MAPPING_CACHE_TIME)
		return data
		
	@staticmethod
	def invalidate(bbs_key):
		memcache.delete(BbsConst.OBJECT_BBS_ID_MAPPING_HEADER+bbs_key)
	
	@staticmethod
	def get_usr_url(host,bbs):
		if(bbs.short):
			return host+""+bbs.short+"/"
		return host+"usr/"+str(bbs.key())+"/"
	
	@staticmethod
	def mapping_host(host):
		if(host=="illust-book.appspot.com"):
			return "www.illustbook.net"
		return host
		
		
	