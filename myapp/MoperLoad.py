#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#MOPERデータのロード

import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from myapp.MesThread import MesThread
from myapp.Bbs import Bbs
from myapp.MappingId import MappingId
from myapp.ChunkManager import ChunkManager

class MoperLoad (webapp.RequestHandler):
	def get(self):
		entry = db.get(self.request.get("id"))
		if entry.image:
			self.response.headers['Content-Type'] = "application/octet-stream"
			if(entry.moper):
				self.response.out.write(entry.moper)
			else:
				if(entry.chunk_list_key):
					ChunkManager.download(self.response.out,entry.chunk_list_key)
					#self.response.out.write(ChunkManager.download(entry.chunk_list_key))
				else:
					self.error(404)
		else:
			self.error(404)
