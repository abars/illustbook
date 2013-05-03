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

	#http://greaterdebater.com/blog/gabe/post/4
	#@staticmethod
	#def auto_link(html):
	#	# match all the urls
	#	# this returns a tuple with two groups
	#	# if the url is part of an existing link, the second element
	#	# in the tuple will be "> or </a>
	#	# if not, the second element will be an empty string
	#	urlre = re.compile("(\(?https?://[-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|])(\">|</a>)?")
	#	urls = urlre.findall(html)
	#	clean_urls = []

	#	# remove the duplicate matches
	#	# and replace urls with a link
	#	for url in urls:
	#		# ignore urls that are part of a link already
	#		if url[1]: continue
	#		c_url = url[0]

	#		# ignore parens if they enclose the entire url
	#		if c_url[0] == '(' and c_url[-1] == ')':
	#			c_url = c_url[1:-1]

	#		if c_url in clean_urls: continue # We've already linked this url

	#		clean_urls.append(c_url)
	#		# substitute only where the url is not already part of a
	#		# link element.
	#		html = re.sub("(?<!(=\"|\">))" + re.escape(c_url), 
	#			"<a rel=\"nofollow\" href=\"" + c_url + "\">" + c_url + "</a>",
	#			html)
	#	return html
