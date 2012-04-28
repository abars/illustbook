//--------------------------------------------------------
//ポータルスクリプト
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

	var page_no=new Object();
	var thread_list=new Object();
	var offset=new Object();
	var page_vec=new Object();
	var page_unit=new Object();
	var requesting=new Object();
	var request_unit=new Object();
	var auto_retry=0;
	var is_iphone;

	var PAGE_N=6;

	function get_ranking(set_is_iphone){
		is_iphone=set_is_iphone;
		var id_list=new Array("ranking_new","ranking_moper","ranking_applause");

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
			page_no[id]=1;
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
	
	function request(id){
		requesting[id]=true;
		var order="";
		var callback;
		if(id=="ranking_new") {order="new";callback=on_loaded_new;}
		if(id=="ranking_moper") {
			if(is_iphone){
				order="bookmark";
			}else{
				order="moper";
			}
			callback=on_loaded_moper;
		}
		if(id=="ranking_applause") {order="applause";callback=on_loaded_applause;}
		illustbook.feed.getThreadList(null,offset[id],request_unit[id],order,callback);
		offset[id]+=request_unit[id];
	}
	
	function on_loaded_new(oj){
		oj=oj.response;
		id="ranking_new";
		on_loaded_core(oj,id);
		if(is_require_next_thread(page_no[id],id)){
		    if(auto_retry<=1){
				auto_retry++;
				request(id);
		    }
		}
	}
	
	function on_loaded_moper(oj){
		oj=oj.response;
		on_loaded_core(oj,"ranking_moper");
	}

	function on_loaded_applause(oj){
		oj=oj.response;
		on_loaded_core(oj,"ranking_applause");
	}

	function on_loaded_core(oj,id){
		requesting[id]=false;
		for(var i=0;i<oj.length;i++){
			thread_list[id].push(oj[i]);
		}
		update(id);
    }
    
    function update(id){
		if(id=="ranking_applause"){
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
    
    function get_text(thread){
		var txt="";
		if(!thread)
		    return txt;
		title=thread.title
		if(title.length>11){
		    title=title.substr(0,10)+"…"
		}
		txt+=""+title+"<BR>";
		txt+=""+thread.author+"<BR>";
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
		
		if(is_iphone){
			txt+="<p>&nbsp</p><p class='page' style='font-size:16px;'>";
		}else{
			txt+="<p class='page'>";
		}
		
		if(page_no[id]>1){
			txt+="<a href='javascript:click_page(\""+id+"\","+(page_no[id]-1)+");'>戻る</a>";
		}
		
		var page_from=page_no[id];
		if(page_vec[id]<0){
			page_from-=4;
		}else{
			page_from-=2;
		}
		if(page_from<1){
			page_from=1;
		}
		var page_to=page_from+PAGE_N;
		for(var page=page_from;page<page_to;page++){
			if(page==page_no[id]){
				txt+="<strong>"+page+"</strong>";
			}else{
				txt+="<a href='javascript:click_page(\""+id+"\","+page+");'>"+page+"</a>"
			}
		}
		
		txt+="<a href='javascript:click_page(\""+id+"\","+(page_no[id]+1)+");'>次へ</a> ";
		txt+="</p>";
		
		document.getElementById(id).innerHTML=txt;
	}
	
	function click_page(id,page){
		if(page>page_no[id]){
			page_vec[id]=1;
		}else{
			page_vec[id]=-1;
		}
		
		if(page<1){
		    page=1;
		}
		
		if(is_require_next_thread(page,id)){
		    if(requesting[id]){
				return;
		    } 
		    page_no[id]=page;
		    update(id);
		    auto_retry=0;
		    request(id);
		}else{
		    page_no[id]=page;
			update(id);
		}
	}
    
    function is_require_next_thread(page,id){
		return (page*page_unit[id]>thread_list[id].length);
    }
