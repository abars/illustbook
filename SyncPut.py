#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#HRD�Ő���������邽�߂�put��A�C���f�b�N�X���X�V�����܂őҋ@����
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db

import logging
import random
import time

class SyncPut():
	@staticmethod
	def put_sync(obj):
		#�قڃ��j�[�N��sand���쐬
		rand=random.randint(0, (1<<30))
		sand=""+str(type(obj))+"_"+str(time.time())+"_"+str(rand)
		
		#put����
		obj.sand=sand	#Model��sand=db.StringProperty()��ǉ����邱��
		obj.put()
	
		#�C���f�b�N�X�ɔ��f�����܂őҋ@
		try_count=1
		for i in range(10):
			#obj�̃I�u�W�F�N�g�S�̂���sand�����I�u�W�F�N�g�̐����擾
			cnt=obj.all().filter("sand =",sand).count()
			if(cnt>=1):
				break
			
			#�܂����f����Ă��Ȃ������̂őҋ@
			time.sleep(1)
			try_count=try_count+1

		#���s�񐔂����M���O
		if(try_count>=3):
			logging.error("put_sync_retry:"+str(try_count))
