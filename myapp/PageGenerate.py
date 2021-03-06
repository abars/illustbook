#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ページ番号生成
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from myapp.BbsConst import BbsConst

class PageGenerate:
	@staticmethod
	def generate_page(page,threads_num,col_num):
		if(threads_num==0):
			threads_num=1
		page_n=BbsConst.PAGE_LIST_COUNT
		page_start = page-page_n/2+1
		if(page_start <= 0):
			page_start = 1
		page_end=page_start+(page_n-1)
		max_page=(threads_num-1)/col_num+1
		if(page_end > max_page):
			page_end=max_page
			page_start=page_end-(page_n-1)
			if(page_start<=0):
				page_start=1
		page_list=range(page_start, (page_end+1))
		return page_list		

