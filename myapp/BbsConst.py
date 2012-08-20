#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#定数定義
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

class BbsConst:
	#掲示板の種別
	BBS_MODE_EVERYONE		=1
	BBS_MODE_ONLY_ADMIN	=2
	BBS_MODE_NO_IMAGE		=3

	#スレッドの種別
	ILLUSTMODE_NONE=0		#thread bbs
	ILLUSTMODE_ILLUST=1		#JPG IMAGE THREAD
	ILLUSTMODE_MOPER=2	#MOPER THREAD
	ILLUSTMODE_TEXT=3		#TEXT ONLY
	
	#アプリの種別
	APP_MODE_APP =0
	APP_MODE_PLUGIN =1
	APP_MODE_CSS =2

	#アプリのサポート掲示板
	APP_SUPPORT_BBS_ID="app_support"
	
	#スパム時のメッセージ
	SPAM_CHECKED ="スパムと判定されました。<BR>通常投稿で表示された場合はabarsceo@gmail.comもしくはサポート掲示板までお問い合わせ下さい。"
	
	#memcacheコントロール
	OBJECT_CACHE_HEADER="ocache24_"	#この値を変更することで全てのキャッシュが無効になる
	OBJECT_BOOKMARK_CACHE_HEADER="bookmark_"
	OBJECT_ENTRY_CACHE_HEADER="entry_"
	OBJECT_BBS_ID_MAPPING_HEADER="map_bbs_"
	OBJECT_THREAD_ID_MAPPING_HEADER="map_thread_"
	
	#memcacheの残存時間
	OBJECT_MAPPING_CACHE_TIME=60*60*24
	OBJECT_CACHE_TIME=60*60*12
	TOPPAGE_FEED_CACHE_TIME=60*60*1
	
	#ranking
	THREAD_RANKING_KEY_NAME="thread_ranking"
	THREAD_RANKING_MAX=100
	THREAD_RANKING_RECENT=2500
	USER_RANKING_MAX=100
	USER_RANKING_RECENT=2500

