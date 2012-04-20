#!-*- coding:utf-8 -*-
#!/usr/bin/env python

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

#-----------------------------------------------
#AppEngineのHRDデータストアで整合性を取る
#-----------------------------------------------

#AppEngineのHRDデータストアはMSデータストアとは異なり、データの整合性が保証されません。
#そのため、putした直後にqueryを投げると、putした要素を取得できません。
#これは、<A HREF="http://d.hatena.ne.jp/sinmetal/20111124/1322098969">インデックスの更新に数十ms～2sec程度</A>かかるためです。
#ということで、put_sync的なメソッドがあるといいのですが、無かったので作りました。

#整合性を取りたいオブジェクトをobj.put()する代わりにSyncPut.put_sync(obj)を使います。
#コンセプトとしては、put()した後、インデックスに反映されるまでquery()を投げ続けます。

#乱数とオブジェクトのキーからsandとなる文字列を作っておき、
#sandでfilterすることで、最新の情報に更新されたかを確認しています。

