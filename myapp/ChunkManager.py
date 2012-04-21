#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#1MBを超えるファイルをチャンク分割して保存する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from myapp.Chunk import Chunk

from google.appengine.ext import db

class ChunkManager ():
	@staticmethod
	def delete(chunk_list):
		for chunk in chunk_list:
			db.delete(db.get(chunk))
	
	@staticmethod
	def upload(data,bbs):
		chunk_list=[]
		
		chunk_size = 500000	#500KBで分割する
		for i in xrange(int(len(data)/chunk_size)+1):
			chunk_data = data[i*chunk_size:(i+1)*chunk_size]
			
			chunk = Chunk()
			chunk.bbs_key=bbs
			chunk.data=chunk_data
			chunk.index=i;
			chunk.put()

			chunk_list.append(db.Key(str(chunk.key()))) 
		
		return chunk_list
	
	@staticmethod
	def download(out,chunk_list):
		#data=None
		for chunk in chunk_list:
			chunk_data=db.get(chunk).data
			out.write(chunk_data)
			
			#メモリ消費が激しいので直接書くことにした
			
			#if(data==None):
			#	data=chunk_data
			#else:
			#	data+=chunk_data
		#return data
