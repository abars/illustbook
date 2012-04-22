//--------------------------------------------------------
//マイページスクリプト
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

function check_id(host){
	var id=document.getElementById("check_short").value;
	window.open(""+host+"check_id?id="+id);
}
	
function confirm_action(url) {
	if (confirm("本当に削除してもよろしいですか?")){
		location.href = url; 
	}	 
}	 

function confirm_action2(url) {
	if (confirm("お絵かき掲示板を削除してもよろしいですか?")){
		confirm_action3(url);
	}	 
}	 

function confirm_action3(url) {
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

//--------------------------------------------------------
//リクエスト
//--------------------------------------------------------

//ページ
var page=0;
var page_unit=12;

//マイページ初期化
var mypage_edit_mode;
var mypage_is_edit=new Object();
var mypage_view_mode;
var mypage_user_id;
var mypage_feed_page;

function mypage_init(tab,login,view_mode,edit_mode,feed_page,is_admin){ 
	mypage_edit_mode=edit_mode;
	mypage_view_mode=view_mode;
	mypage_feed_page=feed_page;
	
	switch(mypage_edit_mode){
	case 6:mypage_is_edit["mypage_bookmark_app"]=1;break;
	case 5:mypage_is_edit["mypage_rental"]=1;break;
	case 4:mypage_is_edit["mypage_follow"]=1;break;
	case 3:mypage_is_edit["mypage_bookmark_bbs"]=1;break;
	case 2:mypage_is_edit["mypage_bookmark_thread"]=1;break;
	}
	
	if(is_admin){
		mypage_is_edit["mypage_rental"]=1;
	}

	var user_id="";
	if(view_mode){
		user_id=illustbook.user.getOwner();
	}else{
		if(login){
			user_id=illustbook.user.getCurrentUser();
		}else{
			return;
		}
	}
	mypage_user_id=user_id;
	
	var offset=0;
	var limit=12;
	var feed_unit=12;

	if(tab=="feed"){
		illustbook.user.getTimeline(user_id,(feed_page-1)*feed_unit,feed_unit,illustbook.user.ORDER_NONE,get_timeline_callback);
	}

	if(tab=="profile"){
		illustbook.user.getBbsList   (user_id,0,limit,illustbook.user.ORDER_NONE,get_user_bbs_list_callback);
		illustbook.user.getThreadList   (user_id,0,limit,illustbook.user.ORDER_NONE,get_user_thread_list_callback);
		illustbook.bookmark.getThreadList(user_id,0,limit,illustbook.bookmark.ORDER_NONE,get_bookmark_thread_list_callback);
		illustbook.bookmark.getBbsList   (user_id,0,limit,illustbook.bookmark.ORDER_NONE,get_bookmark_bbs_list_callback);
	}
	
	illustbook.bookmark.getAppList(user_id,0,limit,illustbook.bookmark.ORDER_NONE,get_bookmark_app_list_callback);
	illustbook.user.getFollow(user_id,0,limit,illustbook.user.ORDER_NONE,get_follow_callback);
	illustbook.user.getFollower(user_id,0,limit,illustbook.user.ORDER_NONE,get_follower_callback);
}

//--------------------------------------------------------
//タイムライン
//--------------------------------------------------------

function get_timeline_callback(oj){
	get_feed(oj,"mypage_feed");
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
	if(feed.from_user){
		txt+='<a href="'+feed.from_user.profile_url+'"><img src="'+feed.from_user.icon_url+'" width=50px height=50px class="radius_image"></a>';
	}else{
		txt+='<img src="static_files/empty_user.png" width=50px height=50px class="radius_image">'
	}
	txt+='</div>'

	//メインブロック
	txt+='<div style="float:left;">'
	
	//ユーザ名
	txt+="<p><b>"
	if(feed.from_user){
		txt+='<a href="'+feed.from_user.profile_url+'">'+feed.from_user.name+'</a>'
	}else{
		txt+='匿名ユーザ'
	}
	if(feed.to_user){
		txt+='　->　<a href="'+feed.to_user.profile_url+'">'+feed.to_user.name+'</A>'
	}
	txt+="</b></p>"
	
	//メッセージ
	txt+="<p>"
	switch(feed.mode){
	case "message":
		txt+=feed.message;
		break;
	case "bbs_new_illust":
		if(feed.thread.thumbnail_url==""){
			txt+='<a href="'+feed.thread.thread_url+'">'+feed.bbs.title+'に記事を投稿しました。</a>'
		}else{
			txt+='<a href="'+feed.thread.thread_url+'">'+feed.bbs.title+'にイラストを投稿しました。</a>'
		}
		break;
	case "new_follow":
		txt+='<a href="'+feed.follow_user.profile_url+'">'+feed.follow_user.name+'をフォローしました。</a>'
		break;
	case "new_bookmark_thread":
		txt+='<a href="'+feed.thread.thread_url+'">'+feed.thread.title+'をブックマークしました。</a>'
		break;
	case "new_comment_thread":
		txt+='<a href="'+feed.thread.thread_url+'">'+feed.thread.title+'にコメントしました。</a>'
		break;
	case "new_bookmark_bbs":
		txt+='<a href="'+feed.bbs.bbs_url+'">'+feed.bbs.title+'をブックマークしました。</a>'
		break;
	}
	txt+="</p>"

	//付加画像データ
	switch(feed.mode){
	case "bbs_new_illust":
		if(feed.thread.thumbnail_url){
			txt+='<a href="'+feed.thread.thread_url+'"><img src="'+feed.thread.thumbnail_url+'" width=100px height=100px></a>'
		}
		break;
	case "new_follow":
		txt+='<a href="'+feed.follow_user.profile_url+'"><img src="'+feed.follow_user.icon_url+'" width=50px height=50px class="radius_image"></a>'
		break;
	case "new_bookmark_thread":
		txt+='<a href="'+feed.thread.thread_url+'"><img src="'+feed.thread.thumbnail_url+'" width=100px height=100px></a>'
		break;
	}
	txt+="</div>"

	//オプション
	txt+='<div style="float:right;text-align:right;">'
	txt+=feed.create_date+"<BR>"
	if(!mypage_view_mode){
		if(feed.mode=="message" && feed.from_user.user_id==mypage_user_id){
			txt+='<a href="#" onclick="if(confirm(\'ツイートを取り消してもよろしいですか？\')){window.location.href=\'feed_tweet?mode=del_tweet&key='+feed.key+'&feed_page='+mypage_feed_page+'\';}return false;">ツイートを取り消す</a><BR>'
		}else{
			txt+='<a href="#" onclick="if(confirm(\'フィードを消去してもよろしいですか？\')){window.location.href=\'feed_tweet?mode=del_feed&key='+feed.key+'&feed_page='+mypage_feed_page+'\';}return false;">フィードを消去</a><BR>'
		}
	}
	txt+="</div>"
	txt+="</div>"
	txt+="<BR CLEAR='all'>"
	txt+="<HR>"

	return txt;
}

//--------------------------------------------------------
//BBSとスレッドとフォロワー
//--------------------------------------------------------

function get_follow_callback(oj){
	get_user(oj,"mypage_follow","フォローしているユーザはいません。");
}

function get_follower_callback(oj){
	get_user(oj,"mypage_follower","フォローされているユーザはいません。");
}

function get_user(oj,id,initial_text){
	if(oj.status!="success"){
		document.getElementById(id).innerHTML="<p>"+oj.message+"</p>";
		return;
	}
	oj=oj.response;
	var txt="";
	for(var i=0;i<oj.length;i++){
		var user=oj[i];
		txt+="<a href='"+user.profile_url+"'>";
		txt+="<img src='"+user.icon_url+"' width=50px height=50px class='radius_image'>";
		txt+="</a>";
		if(id=="mypage_follow" && mypage_is_edit[id]){
			txt+=add_delete_button("del_user&user_key="+user.user_id,0,"フォロー",user.name);
		}
	}
	if(txt==""){
		txt="<p>"+initial_text+"</p>";
	}
	document.getElementById(id).innerHTML=txt;
}

function get_user_bbs_list_callback(oj){
	get_bbs_list(oj,"mypage_rental","レンタルしている掲示板はありません。");
}

function get_bookmark_bbs_list_callback(oj){
	get_bbs_list(oj,"mypage_bookmark_bbs","ブックマークしている掲示板はありません。");
}

function get_bookmark_app_list_callback(oj){
	get_app_list(oj,"mypage_bookmark_app","ブックマークしているアプリはありません。");
}

function get_app_list(oj,id,initial_text){
	if(oj.status!="success"){
		document.getElementById(id).innerHTML="<p>"+oj.message+"</p>";
		return;
	}
	oj=oj.response;
	var txt="";
	for(var i=0;i<oj.length;i++){
		var app=oj[i];
		txt+="<a href='"+app.app_url+"'>";
		txt+="<img src='"+app.icon_url+"' width=50px height=50px class='radius_image'>";		
		txt+="</a>";
		if(mypage_is_edit[id]){
			txt+=add_delete_button("del_app&app_key="+app.key,0,"ブックマーク",app.name);
		}
	}
	if(txt==""){
		txt="<p>"+initial_text+"</p>";
	}
	document.getElementById(id).innerHTML=txt;
}

function get_bbs_list(oj,id,initial_text){
	if(oj.status!="success"){
		document.getElementById(id).innerHTML="<p>"+oj.message+"</p>";
		return;
	}
	oj=oj.response;
	var txt="";
	for(var i=0;i<oj.length;i++){
		var bbs=oj[i];
		txt+="<p><a href='"+bbs.bbs_url+"'>";
		txt+=""+bbs.title;
		if(bbs.bookmark){
			txt+="　";
			txt+="<a href='show_bookmark?bbs_key="+bbs.key+"'>";
			txt+="<small>";
			txt+="("+bbs.bookmark;
			if(bbs.bookmark==1){
				txt+="user";
			}else{
				txt+="users";
			}
			txt+=")";
			txt+="</small>";
			txt+="</a>";
		}
		txt+="</a>";
		if(id=="mypage_bookmark_bbs" && mypage_is_edit[id]){
			txt+=add_delete_button("del_bbs&bbs_key="+bbs.key,0,"ブックマーク",bbs.title);
		}
		if(id=="mypage_rental" && mypage_is_edit[id]){
			txt+=add_delete_button(bbs.key,1,"",bbs.title);
		}
		txt+="</p>";
	}
	if(txt==""){
		txt="<p>"+initial_text+"</p>";
	}
	document.getElementById(id).innerHTML=txt;
}

var thread_list=new Object();

function get_bookmark_thread_list_callback(oj){
	get_thread_list(oj,"mypage_bookmark_thread","ブックマークしているイラストはありません。");
}

function get_user_thread_list_callback(oj){
	get_thread_list(oj,"mypage_submit_thread","投稿したイラストはありません。");
}

function get_thread_list(oj,div_id,message){
	if(oj.status!="success"){
		document.getElementById(div_id).innerHTML="<p>"+oj.message+"</p>";
		return;
	}
	thread_list[div_id]=oj.response;
	update_thread_list(div_id,message);
}

function update_thread_list(div_id,message){
	var oj=thread_list[div_id];
	var txt="";
	var from=0;
	var to=oj.length;
	for(var i=from;i<to;i++){
		var thread=oj[i];
		txt+="<a href='"+thread.thread_url+"'>";
		txt+="<img src='"+thread.thumbnail_url+"' width=100px height=100px>";
		txt+="</a>";
		if(mypage_is_edit["mypage_bookmark_thread"] && div_id=="mypage_bookmark_thread"){
			txt+=add_delete_button("del&thread_key="+thread.key,0,"ブックマーク",thread.title);
		}
	}
	if(oj.length==0 && page==0){
		txt="<p>"+message+"</p>";
	}else{
		if(oj.length==0){
			txt+="<p>Fin.</p>"
		}
		txt+="<BR>"
		txt+="Page."+(page+1)+"　"
		if(page>0){
			txt+=" <a href='javascript:page_change("+(page-1)+",\""+div_id+"\");'>戻る</a>　";
		}
		txt+=" <a href='javascript:page_change("+(page+1)+",\""+div_id+"\");'>次へ</a>";
	}
	document.getElementById(div_id).innerHTML=txt;
}

function get_max_page(div_id){
	return Math.floor((thread_list[div_id].length+(page_unit-1))/page_unit);
}

function page_change(next_page,div_id){
	//if(next_page==get_max_page(div_id)){
	//	next_page=0;
	//}
	page=next_page;
	
	var limit=12;
	document.getElementById(div_id).innerHTML="Loading"
	if(div_id=="mypage_submit_thread"){
		illustbook.user.getThreadList(mypage_user_id,page*limit,limit,illustbook.user.ORDER_NONE,get_user_thread_list_callback);
	}
	if(div_id=="mypage_bookmark_thread"){
		illustbook.bookmark.getThreadList(mypage_user_id,page*limit,limit,illustbook.bookmark.ORDER_NONE,get_bookmark_thread_list_callback);
	}
	//update_thread_list(div_id,"");
}

function add_delete_button(url,rental_mode,prefix,title){
	var txt="<input type='button' value='削除' ";
	txt+="onmouseover=\"this.className='pagebutton_active'\" onmouseout=\"this.className='pagebutton'\" ";
	txt+="class=\"pagebutton\" style=\"font-size:85%\" onclick=\"";
	if(rental_mode){
		txt+="confirm_action2('./del_bbs?bbs_key="+url+"');";
	}else{
		txt+="if(confirm('"+prefix+"から「"+title+"」を削除してもいいですか？')){";
		txt+="window.location.href='./add_bookmark?mode="+url+"'}";
	}
	txt+="\">";
	return txt;
}