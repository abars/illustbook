#!-*- coding:utf-8 -*-
#!/usr/bin/env python

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

#-----------------------------------------------
#AppEngine��HRD�f�[�^�X�g�A�Ő����������
#-----------------------------------------------

#AppEngine��HRD�f�[�^�X�g�A��MS�f�[�^�X�g�A�Ƃ͈قȂ�A�f�[�^�̐��������ۏ؂���܂���B
#���̂��߁Aput���������query�𓊂���ƁAput�����v�f���擾�ł��܂���B
#����́A<A HREF="http://d.hatena.ne.jp/sinmetal/20111124/1322098969">�C���f�b�N�X�̍X�V�ɐ��\ms�`2sec���x</A>�����邽�߂ł��B
#�Ƃ������ƂŁAput_sync�I�ȃ��\�b�h������Ƃ����̂ł����A���������̂ō��܂����B

#����������肽���I�u�W�F�N�g��obj.put()��������SyncPut.put_sync(obj)���g���܂��B
#�R���Z�v�g�Ƃ��ẮAput()������A�C���f�b�N�X�ɔ��f�����܂�query()�𓊂������܂��B

#�����ƃI�u�W�F�N�g�̃L�[����sand�ƂȂ镶���������Ă����A
#sand��filter���邱�ƂŁA�ŐV�̏��ɍX�V���ꂽ�����m�F���Ă��܂��B

