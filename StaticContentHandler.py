#!-*- coding:utf-8 -*-
#!/usr/bin/env python
# NotMofieiedに対応した画像の送信

import cgi
import os
import sys
import re
import datetime

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from Entry import Entry

class StaticContentHandler(webapp.RequestHandler):
  def output_content(self, content, serve=True):
    self.response.headers['Content-Type'] = content.content_type
    last_modified = content.last_modified.strftime(HTTP_DATE_FMT)
    self.response.headers['Last-Modified'] = last_modified
    self.response.headers['ETag'] = '"%s"' % (content.etag,)
    if serve:
      self.response.out.write(content.body)
    else:
      self.response.set_status(304)

  def get(self, path):
    content = get(path)
    if not content:
      self.error(404)
      return

    serve = True
    if 'If-Modified-Since' in self.request.headers:
      last_seen = datetime.datetime.strptime(
          self.request.headers['If-Modified-Since'],
          HTTP_DATE_FMT)
      if last_seen >= content.last_modified.replace(microsecond=0):
        serve = False
    if 'If-None-Match' in self.request.headers:
      etags = [x.strip('" ')
               for x in self.request.headers['If-None-Match'].split(',')]
      if content.etag in etags:
        serve = False
    self.output_content(content, serve)
