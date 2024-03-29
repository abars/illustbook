//--------------------------------------------------------
//ボードスクリプト
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

function bbs_open_draw(url,bbs_key,host){
	var width=document.getElementById("canvas_width").value;
	var height=document.getElementById("canvas_height").value;
	var is_ipad="ipad=1&";
	var url2=''+host+'draw?'+is_ipad+'thread_key=&bbs_key='+bbs_key+'&canvas_width='+width+"&canvas_height="+height+"&canvas_url="+url
	if(is_ipad!=""){
		window.open(url2,false);
	}else{
		window.location.href=url2;
	}
}

function bbs_select_change(order_value,url_base){
	var order=order_value;
	window.location.href=''+url_base+order;
}

function bbs_mute(bbs_key,host,is_english){
	var msg="このボードをミュートして新着に表示されないようにしますか？";
	if(is_english){
		msg="Mute this BBS?";
	}

	var title=is_english ? "Mute":"ミュート";

	jConfirm(msg,title,function(r){
		if(r){
			url=host+"add_bookmark?mode=add_mute_bbs&bbs_key="+bbs_key;
			window.location.href=url;
		}
	});
}

function bbs_add_bookmark(bbs_name,bbs_key,host,is_english){
	var msg='「'+bbs_name+'」をブックマークしますか？';
	if(is_english){
		msg="Add this BBS to your bookmark?"
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
