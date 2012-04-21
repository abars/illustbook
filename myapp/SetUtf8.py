#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#文字コードをUTF8に設定
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import sys

class SetUtf8:
	@staticmethod
	def set():
		stdin = sys.stdin
		stdout = sys.stdout
		reload(sys)
		sys.setdefaultencoding('utf-8')
		sys.stdin = stdin
		sys.stdout = stdout