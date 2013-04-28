#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#コメントをEscapeする
#copyright 2013 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging
import base64

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

class EscapeComment(webapp.RequestHandler):
	@staticmethod
	def escape_br(summary):
		compiled_line = re.compile("\r\n|\r|\n")
		summary = compiled_line.sub(r'<br/>', summary)

		compiled_line = re.compile("<P>|</P>")
		summary = compiled_line.sub(r'', summary)

		return summary

	@staticmethod
	def auto_link(content):
		compiled_line = re.compile("(http://[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)")
		content = compiled_line.sub(r'<a href=\1 target="_blank">\1</a>', content)
		return content

