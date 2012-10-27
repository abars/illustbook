//--------------------------------------------------------
//掲示板スクリプト
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

var isFlashInstalled=function(){if(navigator.plugins["Shockwave Flash"]){return true;}try{new ActiveXObject("ShockwaveFlash.ShockwaveFlash");return true;}catch(a){return false;}}();

function bbs_open_draw(url,bbs_key,host){
	var width=document.getElementById("canvas_width").value;
	var height=document.getElementById("canvas_height").value;
	var is_ipad="";
	if(!isFlashInstalled){
		is_ipad="ipad=1&";
	}
	window.location.href=''+host+'draw?'+is_ipad+'thread_key=&bbs_key='+bbs_key+'&canvas_width='+width+"&canvas_height="+height+"&canvas_url="+url
}

function bbs_open_moper(url,bbs_key,host){
	var width=document.getElementById("canvas_width").value;
	var height=document.getElementById("canvas_height").value;	
	window.location.href=''+host+'draw_moper?thread_key=&bbs_key='+bbs_key+'&canvas_url='+url+'&canvas_width='+width+'&canvas_height='+height
}

function bbs_select_change(order_value,url_base){
	var order=order_value;
	window.location.href=''+url_base+order;
}

function bbs_add_bookmark(bbs_name,bbs_key,host){
	if(confirm('「'+bbs_name+'」をブックマークしますか？')){
		window.location.href=host+"add_bookmark?mode=add_bbs&bbs_key="+bbs_key;
	}
}
