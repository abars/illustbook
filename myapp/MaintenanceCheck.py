#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#AppEngineがメンテナンス中かどうかを取得する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api.capabilities import CapabilitySet
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from google.appengine.api import apiproxy_stub_map

class MaintenanceCheck:
	#メンテナンス中はTrueが返る
	@staticmethod
	def is_appengine_maintenance():
		datastore_readonly = memcache.get("appengine_datastore_readonly")
		if datastore_readonly is None:
			datastore_write = CapabilitySet('datastore_v3', capabilities=['write'])
			datastore_readonly = not datastore_write.is_enabled()
			memcache.set(
			"appengine_datastore_readonly",
			datastore_readonly,
			10*60,
			)
		return datastore_readonly

	#検証用に強制的にメンテナンスモードにする
	#putをフックすることでライト禁止をシミュレートする
	@staticmethod
	def make_datastore_readonly():
		"""Throw ReadOnlyError on put and delete operations."""
		def hook(service, call, request, response):
			assert(service == 'datastore_v3')
			if call in ('Put', 'Delete'):
				raise CapabilityDisabledError('Datastore is in read-only mode')
		apiproxy_stub_map.apiproxy.GetPreCallHooks().Push('readonly_datastore', hook, 'datastore_v3')
