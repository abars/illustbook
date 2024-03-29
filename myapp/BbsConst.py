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
	ILLUSTMODE_MOPER=2		#MOPER THREAD
	ILLUSTMODE_TEXT=3		#TEXT ONLY
	
	#アプリの種別
	APP_MODE_APP =0
	APP_MODE_PLUGIN =1
	APP_MODE_CSS =2

	#アプリのサポート掲示板
	APP_SUPPORT_BBS_ID="app_support"
	
	#スパム時のメッセージ
	SPAM_CHECKED = "スパムと判定されました。コメントを修正して再投稿して下さい。コマントにURLや禁止ワードを含む場合にスパム判定されやすくなります。"
	SPAM_CHECKED_ENGLISH = "Classified as spam. Please remove URL from your comment."

	SPAM_HOST_CHECKED = "ホスト規制されています。規制解除につきましてはabarsceo@gmail.comまでご連絡下さい。ホスト："
	SPAM_HOST_CHECKED_ENGLISH = "Classified as deny host. Host:"
	
	#memcacheコントロール
	OBJECT_CACHE_HEADER="ocache82_"	#この値を変更することで全てのキャッシュが無効になる
	OBJECT_BOOKMARK_CACHE_HEADER="bookmark_"
	OBJECT_ENTRY_CACHE_HEADER="entry_"
	OBJECT_THREAD_CACHE_HEADER="thread_"
	OBJECT_BBS_ID_MAPPING_HEADER="map_bbs_"
	OBJECT_THREAD_ID_MAPPING_HEADER="map_thread_"
	OBJECT_FOLLOWER_HEADER="follower_"
	OBJECT_COUNTER_IP_HEADER="counter_ip_"
	OBJECT_NEW_BBS_CREATING_HEADER="new_bbs_"
	OBJECT_BBS_MESSAGE_HEADER="bbs_message_"
	OBJECT_THREAD_MESSAGE_HEADER="thread_message_"
	OBJECT_BBS_RANKING_HEADER="bbs_ranking_"
	#OBJECT_CHAT_ROOM_HEADER="chat_room_"
	OBJECT_TWEET_LIST_HEADER="tweet_list_"
	
	#memcacheの残存時間
	OBJECT_MAPPING_CACHE_TIME=60*60*24
	OBJECT_CACHE_TIME=60*60*12
	TOPPAGE_FEED_CACHE_TIME=60*60*1
	IMAGE_CACHE_TIME=60*60*3
	SIDEBAR_RECENT_ENTRY_CACHE_TIME=60*60*24
	SIDEBAR_RECENT_THREAD_CACHE_TIME=60*60*24
	COUNTER_IP_CACHE_TIME=60*30
	RECENT_TAG_CACHE_TIME=60*60*24
	NEW_BBS_CACHE_TIME=10
	OBJECT_BBS_MESSAGE_CACHE_TIME=60
	OBJECT_THREAD_MESSAGE_CACHE_TIME=60
	#OBJECT_CHAT_ROOM_CACHE_TIME=60
	OBJECT_TWEET_LIST_CACHE_TIME=180
	
	#tag
	RECENT_TAG_CACHE_HEADER="recent_tag_list_"
	RECENT_TAG_KEY_NAME="recent_tag"

	#ranking
	THREAD_RANKING_KEY_NAME="thread_ranking"
	THREAD_RANKING_MAX=250
	THREAD_RANKING_BEFORE_FILTER_MULT=2	#THREAD_RANKING_MAXのN倍のスレッドをまず取得する
	THREAD_RANKING_RECENT=2500	#この件数だけロギング
	BBS_RANKING_MAX=100
	USER_RANKING_MAX=100
	USER_RANKING_RECENT=2500	#この件数だけロギング
	
	#ページリストの表示数
	PAGE_LIST_COUNT=6
	
	#画像キャッシュ
	IMAGE_CACHE_KEY="image_cache_key_"
	IMAGE_CACHE_DATE="image_cache_date_"
	IMAGE_CACHE_KEY_AND_DATE="image_cache_key_date_"
	
	#スコア
	SCORE_PV=1
	SCORE_APPLAUSE=4
	SCORE_ENTRY=1
	SCORE_RES=1
	SCORE_BOOKMARK=8

	#削除フラグ
	ENTRY_EXIST=1
	ENTRY_DELETED=0

	#スパムチェック用のシード
	SUBMIT_SEED="1212"

	#サムネイル2のバージョン番号、これを変えると新しいサムネイルを生成
	THUMBNAIL2_VERSION=8

	#ピンタレストモードを強制設定するか
	PINTEREST_MODE=2 #1だと管理者だけ、2だと全員
	PINTEREST_PAGE_UNIT=32	#先読み枚数(非表示ユーザがいるので多めに)
	PINTEREST_MYPAGE_PAGE_UNIT=24
	PINTEREST_CACHE_OFFSET=[0,PINTEREST_PAGE_UNIT,PINTEREST_PAGE_UNIT*2,PINTEREST_PAGE_UNIT*3]
	PINTEREST_CACHE_MDOE=["new","hot","monthly"]

	#keyname
	KEY_NAME_TOP_PAGE_CACHE="top_page_cache"
	KEY_NAME_BOOKMARK="bookmark_"

	#thread search
	SEARCH_THREAD_INDEX_NAME="search_thread_index"
	SEARCH_THREAD_VERSION=7

	SEARCH_ENTRY_INDEX_NAME="search_entry_index"
	SEARCH_ENTRY_VERSION=4

	#css custom template
	CSS_CUSTOM=32767

	#アイコン
	USER_ICON_THUMBNAIL_CREATED=1
	USER_ICON_THUMBNAIL_VIOLATE=2

	#イベント
	EVENT_MAX_DAYS=14

	#スパム対策用にログイン必須にするか
	FORCE_LOGIN_TO_CREATE_NEW_IMAGE=True
	FORCE_LOGIN_TO_CREATE_NEW_COMMENT=True




