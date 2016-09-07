//--------------------------------------------------------
//ボードのアクセス解析結果を表示
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

	var cnt_hash;
	var search_list=new Object()

	function sort_func(left,right){
		return cnt_hash[right]-cnt_hash[left];
	}
	
	function get_ranking(txt,is_content_mode,is_english){
		var access_list=txt.split("#")
		
		cnt_hash=new Array()
		var key_list=new Array()
		var key_cnt=0;
		for (var access_no=0;access_no<access_list.length;access_no++){// in access_list){
			var str=access_list[access_no]
			if(str=="")
				continue;
			if(str.match(/admin/))
				continue;
			if(str.match(/analyze/))
				continue;
			if(is_content_mode){
				str=str.split("?")[0]
			}

			var search_engine="検索エンジン"
			if(is_english){
				search_engine="Search Engine"
			}

			var search_str=""
			if(str.match(/.*google.co.jp\/search?.*q=(.*?)&/)){
				search_str=RegExp.$1+"@"+str;
				str=search_engine+"(Google)";
			}
			if(str.match(/.*yahoo.co.jp\/search?.*p=(.*?)&/)){
				search_str=RegExp.$1+"@"+str;
				str=search_engine+"(Yahoo)";
			}	
			if(search_str!=""){
				if(!search_list[search_str]){
					search_list[search_str]=1;
				}else{
					search_list[search_str]++;
				}
			}
			if(!cnt_hash[str]){
				cnt_hash[str]=1;
				key_list[key_cnt]=str
				key_cnt++;
				continue;
			}
			cnt_hash[str]++;
		}
		
		key_list.sort(sort_func)

		var access_txt=""
		for(var i=0;i<key_cnt;i++){
			var list=key_list[i].split("@")
			var txt=list[0];
			var url=list[0];
			if(list.length>=2)
				url=list[1];			
			access_txt+="<p>"+cnt_hash[key_list[i]]+"　<a href='"+url+"' target='_blank' class='decnone'>"+txt.substr(0,64)+"</a></p>";
		}
		
		return access_txt;
	}
	
	function get_search_str(is_english){
		var ret=""
		for(var search in search_list){
			var list=search.split("@")
			var txt=decodeURI(list[0]);
			var url=list[1];
			var cnt=search_list[search];
			var size=Math.floor((Math.log(cnt)/Math.log(10))*20)+15;
			ret+="<a href='"+url+"' target='_blank' class='decnone' style='font-size:"+size+"px'>"+txt+"</font></a>　"
		}
		if(ret==""){
			if(is_english){
				return "<p>No access from search engine</p>";
			}else{
				return "<p>検索エンジンからのアクセスは見つかりませんでした。</p>";
			}
		}
		return ret;
	}
	
	function update(analyze_data,is_english){
		var access_or_content=analyze_data.split("<>")
		write("access",get_ranking(access_or_content[0],false,is_english))
		write("content",get_ranking(access_or_content[1],true,is_english))
		write("search",get_search_str(is_english))
	}
	
	function write(id,value){
		document.getElementById(id).innerHTML=value;
	}	