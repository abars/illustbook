//--------------------------------------------------------
//タイムライン
//copyright 2010-2013 ABARS all rights reserved.
//--------------------------------------------------------

var feed_state=Object();

function feed_set_env(now_tab,view_mode,edit_mode,user_id,feed_page){
	feed_state.now_tab=now_tab;
	feed_state.view_mode=view_mode;
	feed_state.edit_mode=edit_mode;
	feed_state.user_id=user_id;
	feed_state.feed_page=feed_page;
}

function feed_initialize(){
	document.getElementById("feed").innerHTML="<p>Loading</p><p>&nbsp</p>"

	var feed_unit=8;
	if(feed_state.now_tab=="timeline" || feed_state.view_mode){
		illustbook.user.getTimeline(feed_state.user_id,(feed_state.feed_page-1)*feed_unit,feed_unit,illustbook.user.ORDER_NONE,get_timeline_callback);
	}else{
		illustbook.user.getHomeTimeline(feed_state.user_id,(feed_state.feed_page-1)*feed_unit,feed_unit,illustbook.user.ORDER_NONE,get_timeline_callback);
	}

	if(feed_state.feed_page==1){
		$("#feed_previous_page").addClass("disabled2");
	}else{
		$("#feed_previous_page").removeClass("disabled2");
	}
}

function get_timeline_callback(oj){
	get_feed(oj,"feed");
}

function get_feed(oj,id){
	if(oj.status!="success"){
		document.getElementById(id).innerHTML="<p>"+oj.message+"</p>";
		return;
	}
	oj=oj.response;
	if(oj.length==0){
		document.getElementById(id).innerHTML="<p>フィードはありません。</p><p>&nbsp</p>";
		return;
	}
	var txt="<HR>";
	for(var i=0;i<oj.length;i++){
		var feed=oj[i];
		try{
			ret=feed_parse(feed)
		}catch(e){
			ret=""+e+"<BR>"
		}
		txt+=ret
	}
	document.getElementById(id).innerHTML=txt;
}

function feed_parse(feed){
	var txt="";
	
	txt+="<div>"
	
	//アイコン
	txt+='<div style="float:left;width:58px;padding-right:6px;text-align:center;margin:auto;">'
	if(feed.from_user && feed.mode!="deleted"){
		txt+='<a href="javascript:go_feed(\''+feed.from_user.profile_url+'\')"><img src="'+feed.from_user.icon_url+'&size=mini" width="50px" height="50px"/></a>';// class="radius_image"></a>';
	}else{
		txt+='<img src="static_files/empty_user.png" width="50px" height="50px"/>'//' class="radius_image">'
	}
	txt+='</div>'

	//メインブロック
	txt+='<div style="float:left;">'
	
	//ユーザ名
	txt+="<p><b>"
	if(feed.mode!="deleted"){
		if(feed.from_user){
			txt+='<a href="javascript:go_feed(\''+feed.from_user.profile_url+'\')">'+feed.from_user.name+'</a>'
		}else{
			txt+='匿名ユーザ'
		}
		if(feed.to_user){
			txt+='　->　<a href="javascript:go_feed(\''+feed.to_user.profile_url+'\')">'+feed.to_user.name+'</A>'
		}
	}
	txt+="</b></p>"
	
	//メッセージ
	deleted_style_header="<font color='#666'>"
	deleted_style_footer="</font>"
	txt+="<p>"
	switch(feed.mode){
	case "message":
		//txt+=feed.message;
		break;
	case "bbs_new_illust":
		if(!feed.thread.thumbnail_url){
			txt+=deleted_style_header+"投稿したイラストは削除されました。"+deleted_style_footer
		}else{
			if(feed.thread.thumbnail_url==""){
				txt+='<a href="javascript:go_feed(\''+feed.thread.thread_url+'\')">'+feed.bbs.title+'に記事を投稿しました。</a>'
			}else{
				txt+='<a href="javascript:go_feed(\''+feed.thread.thread_url+'\')">'+feed.bbs.title+'にイラストを投稿しました。</a>'
			}
		}
		break;
	case "new_follow":
		txt+='<a href="javascript:go_feed(\''+feed.follow_user.profile_url+'\')">'+feed.follow_user.name+'をフォローしました。</a>'
		break;
	case "new_bookmark_thread":
		txt+='<a href="javascript:go_feed(\''+feed.thread.thread_url+'\')">'+feed.thread.title+'をブックマークしました。</a>'
		break;
	case "new_comment_thread":
		if(!feed.thread){
			txt+=deleted_style_header+"コメントしたイラストは削除されました。"+deleted_style_footer;
			feed.message="";
		}else{
			txt+='<a href="javascript:go_feed(\''+feed.thread.thread_url+'\')">'+feed.thread.title+'にコメントしました。</a>'
		}
		break;
	case "new_bookmark_bbs":
		txt+='<a href="javascript:go_feed(\''+feed.bbs.bbs_url+'\')">'+feed.bbs.title+'をブックマークしました。</a>'
		break;
	case "new_applause_thread":
		txt+='<a href="javascript:go_feed(\''+feed.thread.thread_url+'\')">'+feed.thread.title+'に拍手しました。</a>'
		break;
	}
	txt+="</p>"

	//付加画像データ
	switch(feed.mode){
	case "bbs_new_illust":
		if(feed.thread.thumbnail_url){
			txt+='<a href="javascript:go_feed(\''+feed.thread.thread_url+'\')"><img src="'+feed.thread.thumbnail_url+'" width=100px height=100px></a>'
		}
		break;
	case "new_follow":
		txt+='<a href="javascript:go_feed(\''+feed.follow_user.profile_url+'\')"><img src="'+feed.follow_user.icon_url+'&size=mini" width=50px height=50px class="radius_image"></a>'
		break;
	case "new_applause_thread":
	case "new_bookmark_thread":
		if(feed.thread.thumbnail_url){
			txt+='<a href="javascript:go_feed(\''+feed.thread.thread_url+'\')"><img src="'+feed.thread.thumbnail_url+'" width=100px height=100px></a>'
		}
		break;
	}

	if(feed.message!=""){
		if(feed.mode=="new_comment_thread"){
			txt+='<blockquote><p><a href="javascript:go_feed(\''+feed.thread.thread_url+'\')">'+feed.message+'</a></p></blockquote>';
		}else{
			if(feed.mode=="deleted"){
				txt+="<p>"+deleted_style_header+feed.message+deleted_style_footer+"</p>";
			}else{
				txt+="<p>"+feed.message+"</p>";
			}
		}
	}

	txt+="</div>"

	//オプション
	txt+='<div style="float:right;text-align:right;">'
	txt+=feed.create_date+"<BR>"
	if(!feed_state.view_mode){
		if(feed_state.edit_mode){
			if(feed.from_user.user_id==feed_state.user_id){
				txt+='<a href="#" onclick="if(confirm(\'ツイートを削除してもよろしいですか？\')){window.location.href=\'feed_tweet?mode=del_tweet&key='+feed.key+'&feed_page='+feed_state.feed_page+'&edit=1&tab='+feed_state.now_tab+'\';}return false;" class="g-button mini">削除</a><BR>';
			}else{
				txt+='<a href="#" onclick="if(confirm(\'フィードをタイムラインから除外してもよろしいですか？\')){window.location.href=\'feed_tweet?mode=del_feed&key='+feed.key+'&feed_page='+feed_state.feed_page+'&edit=1&tab='+feed_state.now_tab+'\';}return false;" class="g-button mini">除外</a><BR>'
			}
		}
		if(feed.to_user.user_id==feed_state.user_id){
			txt+='<a href="mypage?user_id='+feed.from_user.user_id+'&tab=feed" class="g-button mini">返信</a><BR>';
		}
	}
	if(feed.from_user.user_id!=feed_state.user_id){
		//txt+='<a href="#" onclick="feed_retweet(\''+feed.key+'\',\''+feed_state.feed_page+'\');return false;" class="g-button mini">リツイート</a><BR>';
	}
	txt+="</div>"
	txt+="</div>"
	txt+="<BR CLEAR='all'>"
	txt+="<HR>"

	return txt;
}

function feed_retweet(feed_key,feed_page){
	var comment=confirm("リツイートしますか？");
	if(!comment){
		return;
	}
	window.location.href='feed_tweet?mode=retweet&key='+feed_key;
}

function go_feed(url){
	var return_url="#feed="+feed_state.feed_page;
	if(window.location.href!=return_url){
		window.location.href=return_url;
	}
	window.location.href=url;
}

function go_feed_next_page(){
	feed_state.feed_page++;
	feed_initialize();
	scroll_to_top();
}

function go_feed_previous_page(){
	if(feed_state.feed_page<=1){
		return;
	}
	feed_state.feed_page--;
	feed_initialize();
	scroll_to_top();
}

function scroll_to_top(){
	$('html, body').animate({scrollTop:0},'fast');
}

