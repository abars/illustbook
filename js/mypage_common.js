function confirm_delete(url,prefix,title,is_english){
	var msg=""+prefix+"から"+title+"を削除してもいいですか？";
	if(is_english){
		msg="Are you sure you want to remove "+title+"?"
	}
	if(confirm(msg)){
		window.location.href="./add_bookmark?mode="+url;
	}
}

function confirm_delete_event(url,is_english){
	var msg="イベントを削除してもいいですか？";
	if(is_english){
		msg="Are you sure you want to remove this event?"
	}
	if(confirm(msg)){
		post_from_url(url);
	}
}

function event_frm_validate(host){
	var sd=document.getElementById("event_start_date").value;
	var ed=document.getElementById("event_end_date").value;
	var id=document.getElementById("event_id").value;
	var md=document.getElementById("event_mode").value;
	window.open(""+host+"event_add?id="+id+"&start_date="+sd+"&end_date="+ed+"&mode="+md);
}

function check_id(host){
	var id=document.getElementById("check_short").value;
	window.open(""+host+"check_id?id="+id);
}

function confirm_action_bbs(url,title,is_english) {
	var msg="ボード「"+title+"」を削除してもよろしいですか?";
	if(is_english){
		msg="Are you sure you want to remove "+title+"?"
	}
	if (confirm(msg)){
		confirm_action_bbs2(url,is_english);
	}	 
}	 

function confirm_action_bbs2(url,is_english) {
	var msg="ボードを一度削除すると復活はできません。本当に削除してもよろしいですか?";
	if(is_english){
		msg="This operation cannot be undone.Are you sure you want to delete this BBS?"
	}
	if (confirm(msg)){
		post_from_url(url)
	}	 
}
		
function confirm_withdraw(url,is_english) {
	var msg="イラストブックから退会しますか？";
	if(is_english){
		msg="Are you sure you want to withdraw from illustbook?"
	}
	if (confirm(msg)){
		msg="退会した場合はブックマーク情報などのユーザ情報が全て削除され復帰できません。本当に削除してもよろしいですか？";
		if(is_english){
			msg="Are you sure you want to clear everything (this operation cannot be undone)?"
		}
		if (confirm(msg)){
			location.href = url; 
		}
	}
}

function confirm_follow(user_key,name,is_english){
	var msg=""+name+"をフォローしますか？";
	if(is_english){
		msg="Are you sure you want to follow "+name+"?";
	}
	if(confirm(msg)){
		location.href="add_bookmark?mode=add_user&user_key="+user_key
	}
}

function confirm_unfollow(user_key,name,is_english){
	var msg=""+name+"のフォローを解除しますか？";
	if(is_english){
		msg="Are you sure you want to remove "+name+"?";
	}
	if(confirm(msg)){
		location.href="add_bookmark?mode=del_user&user_key="+user_key
	}
}

function confirm_mute(user_key,name,is_english){
	var msg=""+name+"をミュートしますか？";
	if(is_english){
		msg="Are you sure you want to mute "+name+"?";
	}
	if(confirm(msg)){
		location.href="add_bookmark?mode=add_mute_user&user_key="+user_key
	}
}

function confirm_remove_tweet_list(is_english){
	var msg='選択したツイートもしくはフィードを削除してもよろしいですか？';
	if(is_english){
		msg="Are you sure you want to remove tweet or feed selected?";
	}
	if(confirm(msg)){
		$("#del_tweet_list").submit();
	}
}

function post_exec(url,data){
	var $form = $('<form/>', {'action': url, 'method': 'post'});
	for(var key in data) {
		$form.append($('<input/>', {'type': 'hidden', 'name': key, 'value': data[key]}));
	}
	$form.appendTo(document.body);
	$form.submit();
}

function post_from_url(get_url){
	var lst=get_url.split("?");
	var url=lst[0];
	lst=lst[1].split("&");
	var data={};
	for(var i=0;i<lst.length;i++){
		var value=lst[i];
		keys=value.split("=")
		data[keys[0]]=keys[1]
	}
	post_exec(url,data);
}

function confirm_remove_tweet_all(user_id,is_english){
	var msg="全てのツイートを削除しますか？";
	if(is_english){
		msg="Are you sure you want to clear everything tweet from illustbook?"
	}
	if (confirm(msg)){
		msg="ツイートは全て削除され復帰できません。本当に削除してもよろしいですか？";
		if(is_english){
			msg="Are you sure you want to clear everything tweet (this operation cannot be undone)?"
		}
		if (confirm(msg)){
			url = 'feed_tweet';
			data={"mode":"del_tweet_all","user_id":user_id} ;
			post_exec(url,data);
		}
	}
}

function show_follower(){
  if($('#follower').is(':visible')){
	$('#follower').hide();
	$('#follower_button').show();  
  }else{
	$('#follower').show();
	$('#follower_button').hide();  
  }
}

function show_profile(is_english){
  var detail="詳細";
  var close="閉じる";
  if(is_english){
	detail="Detail";
	close="Close";
  }
  if($('#profile').is(':visible')){
	$('#profile').hide();
	$('#profile_button').text(detail);
  }else{
   $('#profile').show();  
	$('#profile_button').text(close);
  }
}