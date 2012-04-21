//--------------------------------------------------------
//タグを追加する
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

	function AddTag(host,bbs_key,thread_key){
		window.location.href=host+'add_tag?mode=add&bbs_key='+bbs_key+'&thread_key='+thread_key+'&tag='+GetTag();
	}
	
	function DelTag(host,bbs_key,thread_key){
		window.location.href=host+'add_tag?mode=del&bbs_key='+bbs_key+'&thread_key='+thread_key+'&tag='+GetTag();
	}

	function GetTag(){
		var tag=document.getElementById("tag").value;
		tag=encodeURI(tag);
		return tag;
	}
