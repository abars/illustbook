#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from google.appengine.ext import db
from google.appengine.api import memcache

import re

from Bbs import Bbs
from BbsConst import BbsConst

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
		if(check_id=="code_moper"):
			return 0
		if(check_id=="code_beta"):
			return 0
		if(check_id=="static_files"):
			return 0
		if(check_id=="pressure"):
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
		
		
	