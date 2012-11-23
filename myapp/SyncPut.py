#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#HRDで整合性を取るためにput後、インデックスが更新されるまで待機する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db

import logging
import random
import time

class SyncPut():
	@staticmethod
	def put_sync(obj):
		#ほぼユニークなsandを作成
		rand=random.randint(0, (1<<30))
		sand=""+str(type(obj))+"_"+str(time.time())+"_"+str(rand)
		
		#putする
		obj.sand=sand	#Modelにsand=db.StringProperty()を追加すること
		obj.put()
	
		#インデックスに反映されるまで待機
		try_count=1
		for i in range(10):
			#objのオブジェクト全体からsandを持つオブジェクトの数を取得
			cnt=obj.all().filter("sand =",sand).count()
			if(cnt>=1):
				break
			
			#まだ反映されていなかったので待機
			time.sleep(1)
			try_count=try_count+1

		#試行回数をロギング
		if(try_count>=3):
			logging.error("put_sync_retry:"+str(try_count))
