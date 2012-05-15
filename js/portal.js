//--------------------------------------------------------
//ポータルスクリプト
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

//--------------------------------------------------------
//Ajaxの戻る用
//--------------------------------------------------------

//get_ranking関数が呼ばれる前に呼ばれる

$(function(){
	$(window).hashchange(function(){
		//ハッシュタグが変わった時に実行する処理
		if(location.hash){
			var list=location.hash.split("#")[1].split("_");
			page_no[list[0]]=parseInt(list[1]);
		}
	});
	$(window).hashchange();//Windowロード時に実行
});

//--------------------------------------------------------
//divをidにしたハッシュ
//--------------------------------------------------------

	var PAGE_NO_N=6;

	var page_no=new Object();
	var thread_list=new Object();
	var offset=new Object();
	var page_vec=new Object();
	var page_unit=new Object();
	var requesting=new Object();
	var request_unit=new Object();
	var auto_retry=0;
	var is_iphone;

//--------------------------------------------------------
//初期読込
//--------------------------------------------------------

	function get_ranking(set_is_iphone){
		is_iphone=set_is_iphone;
		var id_list=new Array("news","moper","applause");

		var page_unit_list=new Array(4,3,6);
		var request_unit_list=new Array(4*4,3*2,6*2);
		
		if(is_iphone){
			page_unit_list=new Array(9,9,0)
			request_unit_list=new Array(9*2,9*3,0)
		}

		for(var i=0;i<id_list.length;i++){
			if(page_unit_list[i]==0)
				continue
			var id=id_list[i];
			if(!page_no[id]){
				page_no[id]=1;
			}
			page_vec[id]=1;
			offset[id]=0;
			requesting[id]=0;
			auto_retry=0;
			thread_list[id]=new Array();
			page_unit[id]=page_unit_list[i];
			request_unit[id]=request_unit_list[i];
			request(id);
		}
	}

//--------------------------------------------------------
//サーバからスレッド一覧を取得する
//--------------------------------------------------------

	function request(id){
		requesting[id]=true;
		var order="";
		var callback;
		if(id=="news") {
			order="new";
			callback=on_loaded_new;
		}
		if(id=="moper") {
			if(is_iphone){
				order="bookmark";
			}else{
				order="moper";
			}
			callback=on_loaded_moper;
		}
		if(id=="applause") {
			order="applause";
			callback=on_loaded_applause;
		}
		illustbook.feed.getThreadList(null,offset[id],request_unit[id],order,callback);
		offset[id]+=request_unit[id];
	}

//--------------------------------------------------------
//コールバック
//--------------------------------------------------------

	function on_loaded_new(oj){
		oj=oj.response;
		on_loaded_core(oj,"news");
	}
	
	function on_loaded_moper(oj){
		oj=oj.response;
		on_loaded_core(oj,"moper");
	}

	function on_loaded_applause(oj){
		oj=oj.response;
		on_loaded_core(oj,"applause");
	}

//--------------------------------------------------------
//読み込んできたスレッドをArrayに入れていく
//--------------------------------------------------------

	function on_loaded_core(oj,id){
		//ArrayにPush
		requesting[id]=false;
		for(var i=0;i<oj.length;i++){
			thread_list[id].push(oj[i]);
		}
		
		//Div更新
		update(id);

		//該当ページのデータが取得できるまでリトライする
		if(is_require_next_thread(page_no[id],id)){
			if(auto_retry<=16){
				auto_retry++;
				request(id);
			}
		}
	}

//--------------------------------------------------------
//Divを更新
//--------------------------------------------------------

	function update(id){
		if(id=="applause"){
			update_applause(id);
		}else{
			update_new(id);
		}
	}
	
	function get_link(thread){
		var txt="";
		if(!thread)
			return txt;
		txt+="<a href='"+thread.thread_url+"'>";
		var size=60
		if(is_iphone)
			size=100
		txt+="<img src='"+thread.thumbnail_url+"' BORDER=0 WIDTH="+size+"px HEIGHT="+size+"px></a>";
		return txt;
	}
	
	function limit_str(title){
		if(title.length>11){
			title=title.substr(0,10)+"…"
		}
		return title;
	}
	
	function get_text(thread){
		var txt="";
		if(!thread)
			return txt;
		txt+=""+limit_str(thread.title)+"<BR>";
		txt+=""+limit_str(thread.author)+"<BR>";
		txt+=""+thread.create_date+"<BR>";
		txt+=""+thread.applause+"拍手<BR>";
		return txt;
	}
	
	function update_applause(id){
		var txt="";
		txt+="<div id='clap-prev'>";
		txt+="<a href='javascript:click_page(\""+id+"\","+(page_no[id]-1)+");'>";
		txt+="<img src='static_files/general/images/top/top_clap_prev.gif' alt='' width='25' height='20' /></a></div>";
		for(var i=0;i<page_unit[id];i++){
			var thread=thread_list[id][i+page_unit[id]*(page_no[id]-1)];
			if(!thread)
				continue;
			txt+="<div class='clap-thum'>";
			txt+=get_link(thread)+"<BR>";
			txt+=get_text(thread)+"<BR>";
			txt+="</div>";
		}

		txt+="<div id='clap-next'>";
		txt+="<a href='javascript:click_page(\""+id+"\","+(page_no[id]+1)+");'>";
		txt+="<img src='static_files/general/images/top/top_clap_next.gif' alt='' width='25' height='20' /></a></div>";

		document.getElementById(id).innerHTML=txt;
	}
	
	function get_page_from(id){
		var page_from=page_no[id];
		if(page_vec[id]<0){
			page_from-=4;
		}else{
			page_from-=2;
		}
		if(page_from<1){
			page_from=1;
		}
		return page_from;
	}
	
	function add_page_list(id){
		var txt="";
		
		if(is_iphone){
			txt+="<p>&nbsp</p><p class='page' style='font-size:16px;'>";
		}else{
			txt+="<p class='page'>";
		}
		
		if(page_no[id]>1){
			txt+="<a href='javascript:click_page(\""+id+"\","+(page_no[id]-1)+");'>戻る</a>";
		}
		
		var page_from=get_page_from(id);
		var page_to=page_from+PAGE_NO_N;

		for(var page=page_from;page<page_to;page++){
			if(page==page_no[id]){
				txt+="<strong>"+page+"</strong>";
			}else{
				txt+="<a href='javascript:click_page(\""+id+"\","+page+");'>"+page+"</a>"
			}
		}
		
		txt+="<a href='javascript:click_page(\""+id+"\","+(page_no[id]+1)+");'>次へ</a> ";
		txt+="</p>";
		
		return txt;
	}
	
	function update_new(id){
		var txt="<dl>";
		for(var i=0;i<page_unit[id];i++){
			var thread=thread_list[id][i+page_unit[id]*(page_no[id]-1)];
			if(is_iphone){
				txt+=get_link(thread);
				continue
			}
			txt+="<dt>";
			txt+=get_link(thread);
			txt+="</dt>";
			txt+="<dd>";
			txt+=get_text(thread);
			txt+="</dd>";
		}
		txt+="</dl>";
		
		txt+=add_page_list(id);

		document.getElementById(id).innerHTML=txt;
	}

//--------------------------------------------------------
//ページ遷移
//--------------------------------------------------------

	function click_page(id,page){
		//ページ番号一覧の方向用
		if(page>page_no[id]){
			page_vec[id]=1;
		}else{
			page_vec[id]=-1;
		}
		
		//リミット
		if(page<1){
			page=1;
		}
		
		//サーバから追加で読み込んでくる必要があるか？
		var require_next_thread=is_require_next_thread(page,id);
		if(require_next_thread){
			if(requesting[id]){
				return;
			}
		}
		
		//ページ遷移
		page_no[id]=page;
		window.location.href="#"+id+"_"+page;
		update(id);
		
		//次のデータの要求を出しておく
		if(require_next_thread){
			auto_retry=0;
			request(id);
		}
	}
	
	function is_require_next_thread(page,id){
		return (page*page_unit[id]>thread_list[id].length);
	}
