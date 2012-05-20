//--------------------------------------------------------
//マイページスクリプト
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

//--------------------------------------------------------
//Ajaxの戻る用
//--------------------------------------------------------

//get_ranking関数が呼ばれる前に呼ばれる

var mypage_page=new Object();
var initial_load=true;

function hashchange_core(id,page){
	if(mypage_page[id]!=page){
		mypage_page[id]=page;
		if(!initial_load){
			page_change_core(mypage_page[id],id);
		}
	}
}

$(function(){
	$(window).hashchange(function(){
		//ハッシュタグが変わった時に実行する処理
		if(location.hash){
			var list=location.hash.split("#")[1].split("=");
			hashchange_core(list[0],parseInt(list[1])-1);
		}else{
			hashchange_core("submit_thread",0);
			hashchange_core("bookmark_thread",0);
		}
	});
	$(window).hashchange();//Windowロード時に実行
});

//--------------------------------------------------------
//レンタル系
//--------------------------------------------------------

function check_id(host){
	var id=document.getElementById("check_short").value;
	window.open(""+host+"check_id?id="+id);
}

/*
function confirm_action(url) {
	if (confirm("本当に削除してもよろしいですか?")){
		location.href = url; 
	}	 
}	 
*/

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

//--------------------------------------------------------
//リクエスト
//--------------------------------------------------------

//ページ
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
	case 6:mypage_is_edit["bookmark_app"]=1;break;
	case 5:mypage_is_edit["rental"]=1;break;
	case 4:mypage_is_edit["follow"]=1;break;
	case 3:mypage_is_edit["bookmark_bbs"]=1;break;
	case 2:mypage_is_edit["bookmark_thread"]=1;break;
	}
	
	if(is_admin){
		mypage_is_edit["rental"]=1;
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

	var offset_bookmark=mypage_page["bookmark_thread"]
	var offset_submit=mypage_page["submit_thread"]
	if(offset_bookmark){offset_bookmark*=limit;}else{offset_bookmark=0;}
	if(offset_submit){offset_submit*=limit;}else{offset_submit=0;}

	if(tab=="profile"){
		illustbook.user.getBbsList(user_id,0,limit,illustbook.user.ORDER_NONE,get_user_bbs_list_callback);
		illustbook.user.getThreadList(user_id,offset_submit,limit,illustbook.user.ORDER_NONE,get_user_thread_list_callback);
		illustbook.bookmark.getThreadList(user_id,offset_bookmark,limit,illustbook.bookmark.ORDER_NONE,get_bookmark_thread_list_callback);
		illustbook.bookmark.getBbsList(user_id,0,limit,illustbook.bookmark.ORDER_NONE,get_bookmark_bbs_list_callback);
	}
	
	illustbook.bookmark.getAppList(user_id,0,limit,illustbook.bookmark.ORDER_NONE,get_bookmark_app_list_callback);
	illustbook.user.getFollow(user_id,0,limit,illustbook.user.ORDER_NONE,get_follow_callback);
	illustbook.user.getFollower(user_id,0,limit,illustbook.user.ORDER_NONE,get_follower_callback);
	
	initial_load=false;
}

//--------------------------------------------------------
//タイムライン
//--------------------------------------------------------

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
	get_user(oj,"follow","フォローしているユーザはいません。");
}

function get_follower_callback(oj){
	get_user(oj,"follower","フォローされているユーザはいません。");
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
		txt+="<div style='position:relative;float:left;'>";
		txt+="<a href='"+user.profile_url+"'>";
		txt+="<img src='"+user.icon_url+"' width=50px height=50px class='radius_image'>";
		txt+="</a>";
		if(id=="follow" && mypage_is_edit[id]){
			txt+="<div style='position:absolute;top:0px;left:0px;'>";
			txt+=add_delete_button("del_user&user_key="+user.user_id,0,"フォロー",user.name);
			txt+="</div>";
		}
		txt+="</div>";
	}
	if(txt==""){
		txt="<p>"+initial_text+"</p>";
	}
	document.getElementById(id).innerHTML=txt;
}

function get_user_bbs_list_callback(oj){
	get_bbs_list(oj,"rental","レンタルしている掲示板はありません。");
}

function get_bookmark_bbs_list_callback(oj){
	get_bbs_list(oj,"bookmark_bbs","ブックマークしている掲示板はありません。");
}

function get_bookmark_app_list_callback(oj){
	get_app_list(oj,"bookmark_app","ブックマークしているアプリはありません。");
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
		txt+="<div style='position:relative;float:left;'>";
		txt+="<a href='"+app.app_url+"'>";
		txt+="<img src='"+app.icon_url+"' width=50px height=50px class='radius_image'>";		
		txt+="</a>";
		if(mypage_is_edit[id]){
			txt+="<div style='position:absolute;left:0px;top:0px;'>";
			txt+=add_delete_button("del_app&app_key="+app.key,0,"アプリ",app.name);
			txt+="</div>";
		}
		txt+="</div>";
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
		
		//サムネイルと削除ボタン
		txt+="<div style='position:relative;float:left;width:60px;height:52px;padding-top:2px;'>"
		if(bbs.thumbnail_url){
			txt+="<a href='"+bbs.bbs_url+"'>";
			txt+="<img src='"+bbs.thumbnail_url+"' width=50px height=50px class='radius_image'>";
			txt+="</a>";
		}
		if(id=="bookmark_bbs" && mypage_is_edit[id]){
			txt+="<div style='position:absolute;left:0px;top:0px;'>";
			txt+=add_delete_button("del_bbs&bbs_key="+bbs.key,0,"ブックマーク",bbs.title);
			txt+="</div>";
		}
		if(id=="rental" && mypage_is_edit[id]){
			txt+="<div style='position:absolute;left:0px;top:0px;'>";
			txt+=add_delete_button(bbs.key,1,"",bbs.title);
			txt+="</div>";
		}
		txt+="</div>";
		
		//基本情報
		txt+="<div style='float:left;padding-top:18px;'>";
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
		txt+="</p>";
		txt+="</div><br clear='all'>";
	}
	if(txt==""){
		txt="<p>"+initial_text+"</p>";
	}
	document.getElementById(id).innerHTML=txt;
}

var thread_list=new Object();

function get_bookmark_thread_list_callback(oj){
	get_thread_list(oj,"bookmark_thread","ブックマークしているイラストはありません。");
}

function get_user_thread_list_callback(oj){
	get_thread_list(oj,"submit_thread","投稿したイラストはありません。");
}

function get_thread_list(oj,div_id,message){
	if(oj.status!="success"){
		document.getElementById(div_id).innerHTML="<p>"+oj.message+"</p>";
		return;
	}
	thread_list[div_id]=oj.response;
	update_thread_list(div_id,message);
}

function go_thread(url,id){
	var return_url="#"+id+"="+(mypage_page[id]+1);
	if(window.location.href!=return_url && mypage_page[id]!=0){
		window.location.href=return_url;
	}
	window.location.href=url;
}

function update_thread_list(div_id,message){
	var oj=thread_list[div_id];
	var txt="";
	var from=0;
	var to=oj.length;
	for(var i=from;i<to;i++){
		var thread=oj[i];
		txt+="<div style='position:relative;float:left;width:100px;height:100px'><a href='javascript:go_thread(\""+thread.thread_url+"\",\""+div_id+"\");'>";
		txt+="<img src='"+thread.thumbnail_url+"' width=100px height=100px class='radius_image'>";// style='display:none;' onload='$(this).fadeIn(250);'>";
		txt+="</a>";
		if(mypage_is_edit["bookmark_thread"] && div_id=="bookmark_thread"){
			txt+="<div style='position:absolute;left:0px;top:0px;'>";
			txt+=add_delete_button("del&thread_key="+thread.key,0,"ブックマーク",thread.title);
			txt+="</div>";
		}
		txt+="</div>";
	}
	var page=mypage_page[div_id];
	if(!page){
		page=0;
	}
	if(oj.length==0 && page==0){
		txt="<p>"+message+"</p>";
	}else{
		if(oj.length==0){
			txt+="<p>Fin.</p>"
		}
		txt+="<BR clear='all'>"
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
	page_change_core(next_page,div_id);
}

function page_change_core(next_page,div_id){
	mypage_page[div_id]=next_page;
	
	var limit=12;
	$("#"+div_id).append("<img src='static_files/loading.gif'>");
	if(div_id=="submit_thread"){
		illustbook.user.getThreadList(mypage_user_id,mypage_page[div_id]*limit,limit,illustbook.user.ORDER_NONE,get_user_thread_list_callback);
	}
	if(div_id=="bookmark_thread"){
		illustbook.bookmark.getThreadList(mypage_user_id,mypage_page[div_id]*limit,limit,illustbook.bookmark.ORDER_NONE,get_bookmark_thread_list_callback);
	}
}

function add_delete_button(url,rental_mode,prefix,title){
	var txt="<input type='button' value='X' ";
	txt+="onmouseover=\"this.className='pagebutton_active'\" onmouseout=\"this.className='pagebutton'\" ";
	txt+="class=\"pagebutton\" style=\"font-size:85%\" onclick=\"";
	if(rental_mode){
		txt+="confirm_action_bbs('./del_bbs?bbs_key="+url+"','"+title+"');";
	}else{
		txt+="if(confirm('"+prefix+"から「"+title+"」を削除してもいいですか？')){";
		txt+="window.location.href='./add_bookmark?mode="+url+"'}";
	}
	txt+="\">";
	return txt;
}
