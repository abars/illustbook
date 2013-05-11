//--------------------------------------------------------
//タイムライン
//copyright 2010-2013 ABARS all rights reserved.
//--------------------------------------------------------

function feed_set_env(now_tab,view_mode,edit_mode,user_id,feed_page){
}

function feed_initialize(){
}

function feed_retweet(feed_key,feed_page){
	var comment=confirm("リツイートしますか？");
	if(!comment){
		return;
	}
	window.location.href='feed_tweet?mode=retweet&key='+feed_key;
}

