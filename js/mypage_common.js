function confirm_delete(url,prefix,title,is_english){
	var msg=""+prefix+"から「"+title+"」を削除してもいいですか？";
	if(is_english){
		msg="Are you sure you want to remove "+title+"?"
	}
	if(confirm(msg)){
		window.location.href="./add_bookmark?mode="+url;
	}
}

function check_id(host){
	var id=document.getElementById("check_short").value;
	window.open(""+host+"check_id?id="+id);
}

function confirm_action_bbs(url,title,is_english) {
	var msg="お絵かき掲示板「"+title+"」を削除してもよろしいですか?";
	if(is_english){
		msg="Are you sure you want to remove "+title+"?"
	}
	if (confirm(msg)){
		confirm_action_bbs2(url,is_english);
	}	 
}	 

function confirm_action_bbs2(url,is_english) {
	var msg="お絵かき掲示板を一度削除すると復活はできません。本当に削除してもよろしいですか?";
	if(is_english){
		msg="This operation cannot be undone.Are you sure you want to delete this BBS?"
	}
	if (confirm(msg)){
		location.href = url; 
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

function confirm_remove_tweet_all(user_id,is_english){
	var msg="全てのツイートとフィードを削除しますか？";
	if(is_english){
		msg="Are you sure you want to withdraw from illustbook?"
	}
	if (confirm(msg)){
		msg="ツイートとフィードは全て削除され復帰できません。本当に削除してもよろしいですか？";
		if(is_english){
			msg="Are you sure you want to clear everything tweet and feed (this operation cannot be undone)?"
		}
		if (confirm(msg)){
			location.href = 'feed_tweet?mode=del_tweet_all&user_id='+user_id; 
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