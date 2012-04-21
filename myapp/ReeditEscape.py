#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#再編集用のテキストエスケープ
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

import re
import os

from MesThread import MesThread

class ReeditEscape:
	@staticmethod
	def escape(text):
		text=text.replace("'","`");
		compiled_line = re.compile("\r\n|\r|\n")
		text=compiled_line.sub(r'', text)
		return text



