function confirm_delete(url,prefix,title){
	if(confirm(""+prefix+"から「"+title+"」を削除してもいいですか？")){
		window.location.href="./add_bookmark?mode="+url;
	}
}

function check_id(host){
	var id=document.getElementById("check_short").value;
	window.open(""+host+"check_id?id="+id);
}

function confirm_action_bbs(url,title) {
	if (confirm("お絵かき掲示板「"+title+"」を削除してもよろしいですか?")){
		confirm_action_bbs2(url);
	}	 
}	 

function confirm_action_bbs2(url) {
	if (confirm("お絵かき掲示板を一度削除すると復活はできません。本当に削除してもよろしいですか?")){
		location.href = url; 
	}	 
}
		
function confirm_withdraw(url) {
	if (confirm("イラストブックから退会しますか？")){
		if (confirm("退会した場合はブックマーク情報などのユーザ情報が全て削除され復帰できません。本当に削除してもよろしいですか？")){
			location.href = url; 
		}
	}
}
