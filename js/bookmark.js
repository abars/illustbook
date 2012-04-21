//--------------------------------------------------------
//ブックマークしているユーザを表示する
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

	function request_user_list(thread_key,bbs_key,app_key){
		if(thread_key!=""){
			illustbook.request.get("api_bookmark?method=getThreadUserList&thread_key="+thread_key,user_callback);
		}
		if(bbs_key!=""){
			illustbook.request.get("api_bookmark?method=getBbsUserList&bbs_key="+bbs_key,user_callback);
		}
		if(app_key!=""){
			illustbook.request.get("api_bookmark?method=getAppUserList&app_key="+app_key,user_callback);
		}
	}
	
	function user_callback(oj){
		oj=oj.response;
		var txt="";
		for(var i=0;i<oj.length;i++){
			var user=oj[i];
			txt+="<div style='float:left;'>";
			txt+="<A HREF='mypage?user_id="+user.user_id+"'>";
			txt+="<IMG SRC='"+user.icon_url+"' WIDTH=50px HEIGHT=50px class='radius_image'>";
			txt+="</A>";
			txt+="</div>";
		}
		if(oj.length==0){
			txt="<p>該当するユーザが見つかりませんでした。</p>";
		}
		document.getElementById("user_list").innerHTML=txt;
	}
