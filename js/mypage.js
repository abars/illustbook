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
var initial_tab=null;

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
			if(list[0]=="submit_thread" || list[0]=="bookmark_thread"){
				initial_tab="illust";
			}
			if(list[0]=="feed"){
				initial_tab="feed";
			}
			if(list[0]=="bbs"){
				initial_tab="illust";
			}
		}else{
			hashchange_core("submit_thread",0);
			hashchange_core("bookmark_thread",0);
		}
	});
	$(window).hashchange();//Windowロード時に実行
});

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
var mypage_initialized=new Object();
var mypage_now_tab;

var illust_limit=12;
var g_is_iphone=0;

function mypage_init(tab,login,view_mode,edit_mode,feed_page,is_admin,is_iphone){ 
	//ハッシュ値から計算したタブ
	if(initial_tab){
		tab=initial_tab;
	}

	//ステートを保持
	g_is_iphone=is_iphone;
	mypage_edit_mode=edit_mode;
	mypage_view_mode=view_mode;
	mypage_feed_page=feed_page;

	if(mypage_edit_mode){
		mypage_is_edit["bookmark_app"]=1;
		mypage_is_edit["rental"]=1;
		mypage_is_edit["follow"]=1;
		mypage_is_edit["bookmark_bbs"]=1;
		mypage_is_edit["bookmark_thread"]=1;
	}
	
	if(is_admin){
		mypage_is_edit["rental"]=1;
	}
	if(is_iphone){
		illust_limit=9;
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

	//illustbook.request.beginPackedRequest();
	//illustbook.request.endPackedRequest();
	
	initial_load=false;

	display_tab(tab);

	if(!is_iphone){
		user_initialize();
	}
}

function user_initialize(){
	var limit=illust_limit;
	var user_id=mypage_user_id;
	illustbook.bookmark.getAppList(user_id,0,limit,illustbook.bookmark.ORDER_NONE,get_bookmark_app_list_callback);
	if(mypage_edit_mode){
		illustbook.user.getFollow(user_id,0,limit,illustbook.user.ORDER_NONE,get_follow_callback);
		illustbook.user.getFollower(user_id,0,limit,illustbook.user.ORDER_NONE,get_follower_callback);
	}else{
		illustbook.user.getFollowFast(user_id,0,limit,illustbook.user.ORDER_NONE,get_follow_callback);
		illustbook.user.getFollowerFast(user_id,0,limit,illustbook.user.ORDER_NONE,get_follower_callback);
	}
}

function illust_initialize(){
	var offset=0;
	var limit=illust_limit;

	var offset_bookmark=mypage_page["bookmark_thread"]
	var offset_submit=mypage_page["submit_thread"]
	if(offset_bookmark){offset_bookmark*=limit;}else{offset_bookmark=0;}
	if(offset_submit){offset_submit*=limit;}else{offset_submit=0;}

	illustbook.user.getThreadList(mypage_user_id,offset_submit,limit,illustbook.user.ORDER_NONE,get_user_thread_list_callback);
	illustbook.bookmark.getThreadList(mypage_user_id,offset_bookmark,limit,illustbook.bookmark.ORDER_NONE,get_bookmark_thread_list_callback);
	illustbook.user.getBbsList(mypage_user_id,0,limit,illustbook.user.ORDER_NONE,get_user_bbs_list_callback);
	illustbook.bookmark.getBbsList(mypage_user_id,0,limit,illustbook.bookmark.ORDER_NONE,get_bookmark_bbs_list_callback);
}

function go_edit_mode(edit_mode){
	var edit_sufix="&edit=1"
	if(edit_mode){
		edit_sufix=""
	}
	window.location.href="./mypage?tab="+mypage_now_tab+edit_sufix;
}

function display_tab(id){
	mypage_now_tab=id;

	feed_set_env(mypage_now_tab,mypage_view_mode,mypage_edit_mode,mypage_user_id,mypage_feed_page);

	if(id=="timeline" || id=="home_timeline"){
		id="feed";
	}

	$(".one_tab").hide();
	$("#one_tab_"+id).show();
		
	$(".g-button").removeClass("checked");
	$("#"+id+"_tab").addClass("checked");

	if(!mypage_initialized[id]){
		if(id=="illust"){
			illust_initialize();
		}
		if(id=="profile"){
			if(g_is_iphone){
				user_initialize();
			}
		}
		if(id=="feed"){
			feed_initialize();
		}
		mypage_initialized[id]=true;
	}
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
		txt+="<img src='"+user.icon_url+"&size=mini' width=50px height=50px class='radius_image'>";
		txt+="</a>";
		if(id=="follow" && mypage_is_edit[id]){
			txt+=add_delete_button("del_user&user_key="+user.user_id,0,"フォロー",user.name);
		}
		txt+="</div>";
	}
	if(txt==""){
		txt=""+initial_text+"";
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
			txt+=add_delete_button("del_app&app_key="+app.key,0,"アプリ",app.name);
		}
		txt+="</div>";
	}
	if(txt==""){
		txt=""+initial_text+"";
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
		
		txt+="<div style='width:310px;float:left;'>";
		
		//サムネイルと削除ボタン
		txt+="<div style='position:relative;float:left;width:60px;height:52px;padding-top:2px;'>"
			if(bbs.thumbnail_url){
				txt+="<a href='javascript:go_bbs(\""+bbs.bbs_url+"\")'>";
				txt+="<img src='"+bbs.thumbnail_url+"' width=50px height=50px class='radius_image'>";
				txt+="</a>";
			}
			if(id=="bookmark_bbs" && mypage_is_edit[id]){
				txt+=add_delete_button("del_bbs&bbs_key="+bbs.key,0,"ブックマーク",bbs.title);
			}
			if(id=="rental" && mypage_is_edit[id]){
				txt+=add_delete_button(bbs.key,1,"",bbs.title);
			}
		txt+="</div>";
		
		//基本情報
		txt+="<div style='float:left;padding-top:18px;width:240px;'>";
			txt+="<div style='float:left;width:170px;margin-right:10px;''><p><a href='javascript:go_bbs(\""+bbs.bbs_url+"\")'>";
			txt+=""+bbs.title;
			txt+="</a></p></div>";
			txt+="<div style='float:left;'>"
		
			if(bbs.bookmark){
				txt+="<a href='show_bookmark?bbs_key="+bbs.key+"' class='g-button no-text'>";
				txt+='<i class="icon-star"></i>';
				txt+=bbs.bookmark;
				txt+="</a>";
			}else{
				//txt+="-";
			}
			txt+="</div>"
		txt+="</div>";

		txt+="</div>";
		if(i%2==1){
			txt+="<br clear='all'>";
		}
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
	var page_no=1;
	if(mypage_page[id]){
		page_no=mypage_page[id]+1;
	}
	var return_url="#"+id+"="+page_no;
	if(window.location.href!=return_url){//} && mypage_page[id]!=0){
		window.location.href=return_url;
	}
	window.location.href=url;
}

function go_bbs(url){
	var return_url="#bbs=1";
	if(window.location.href!=return_url){
		window.location.href=return_url;
	}
	window.location.href=url;
}

function update_thread_list(div_id,message){
	var oj=thread_list[div_id];
	var txt="<div style='max-width:800px;'>";
	var from=0;
	var to=oj.length;
	for(var i=from;i<to;i++){
		var thread=oj[i];
		var size=100;
		if(g_is_iphone){
			size=95;
		}
		txt+="<div style='position:relative;float:left;width:"+size+"px;height:"+size+"px;margin:2px;box-shadow: 0 0 3px #cccccc;'><a href='javascript:go_thread(\""+thread.thread_url+"\",\""+div_id+"\");'>";
		txt+="<img src='"+thread.thumbnail_url+"' width="+size+"px height="+size+"px style='display:none;' onload='$(this).fadeIn(500);'>";
		txt+="</a>";
		if(mypage_is_edit["bookmark_thread"] && div_id=="bookmark_thread"){
			txt+=add_delete_button("del&thread_key="+thread.key,0,"ブックマーク",thread.title);
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

		txt+='<br clear="all"><div class="g-button-group" style="float:right;">';
		if(page==0){
			txt+='<a href="#" class="g-button no-text disabled2"><i class="icon-chevron-left"></i></a>';
		}else{
			txt+='<a href="javascript:page_change('+(page-1)+',\''+div_id+'\');" class="g-button no-text"><i class="icon-chevron-left"></i></a>';
		}
		txt+='<a href="javascript:page_change('+(page+1)+',\''+div_id+'\');" class="g-button no-text"><i class="icon-chevron-right"></i></a>';
		txt+='</div><br clear="all">';
	}
	txt+="</div>"
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
	
	var limit=illust_limit;
	$("#"+div_id).append("<img src='static_files/loading.gif'>");
	if(div_id=="submit_thread"){
		illustbook.user.getThreadList(mypage_user_id,mypage_page[div_id]*limit,limit,illustbook.user.ORDER_NONE,get_user_thread_list_callback);
	}
	if(div_id=="bookmark_thread"){
		illustbook.bookmark.getThreadList(mypage_user_id,mypage_page[div_id]*limit,limit,illustbook.bookmark.ORDER_NONE,get_bookmark_thread_list_callback);
	}
}

function add_delete_button(url,rental_mode,prefix,title){
	var script="";
	if(rental_mode){
		script+="confirm_action_bbs('./del_bbs?bbs_key="+url+"','"+title+"');";
	}else{
		script="confirm_delete('"+url+"','"+prefix+"','"+title+"')";
	}
	var txt="";
	txt+='<a href="javascript:'+script+';" class="g-button no-text delete_button"><i class="icon-remove"></i></a>';
	return txt;
}

