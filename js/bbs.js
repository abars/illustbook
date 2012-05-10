//--------------------------------------------------------
//掲示板スクリプト
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

function bbs_open_draw(url,bbs_key,host){
	var width=document.getElementById("canvas_width").value;
	var height=document.getElementById("canvas_height").value;	
	window.location.href=''+host+'draw?thread_key=&bbs_key='+bbs_key+'&canvas_width='+width+"&canvas_height="+height+"&canvas_url="+url
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
