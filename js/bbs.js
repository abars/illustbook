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
	var url2=''+host+'draw?'+is_ipad+'thread_key=&bbs_key='+bbs_key+'&canvas_width='+width+"&canvas_height="+height+"&canvas_url="+url
	if(is_ipad!=""){
		window.open(url2,false);
	}else{
		window.location.href=url2;
	}
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

function bbs_add_bookmark(bbs_name,bbs_key,host,is_english){
	var msg='「'+bbs_name+'」をブックマークしますか？';
	if(is_english){
		msg="Are you bookmark this BBS?"
	}

	var title=is_english ? "Bookmark":"ブックマーク";

	jConfirm(msg,title,function(r){
		if(r){
			msg=is_english ? "processing":"ブックマークしています。";
			jAlert(msg,title);
			$('#popup_ok').hide();

			url=host+"add_bookmark?mode=add_bbs&bbs_key="+bbs_key;

			//window.location.href=url;
			$.get(url, function(data){
				var msg=is_english ? "success":"ブックマークに成功しました。";
				jAlert(msg,title);
			});
		}
	});
}

function bbs_open_ipad_canvas_size(){
	if($('#ipad_canvas_size').is(':visible')){
		$("#ipad_canvas_size").hide();
	}else{
		$("#ipad_canvas_size").show();
	}
}
