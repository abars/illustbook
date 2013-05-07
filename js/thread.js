//--------------------------------------------------------
//スレッドスクリプト
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

var isFlashInstalled=function(){if(navigator.plugins["Shockwave Flash"]){return true;}try{new ActiveXObject("ShockwaveFlash.ShockwaveFlash");return true;}catch(a){return false;}}();

		function select_change(order_value,url_base,page,limit){
			var order=order_value;
			window.location.href=''+url_base+page+"&order="+order+"&limit="+limit;
		}

		function confirm_action_comment(url) {
			if (confirm("本当にコメントを削除しますか?")){
				location.href = url; 
			}
		}

		function confirm_action_term(url) {
			if (confirm("本当に規約設定を変更しますか?")){
				location.href = url; 
			}
		}

		function confirm_action_thread(th, bbs, host) {
			if (confirm("本当に削除しますか?")){
				if (confirm("削除したデータは復元できません。本当に削除しますか?")){
					location.href = ""+host+"del_thread?thread_key="+th+"&bbs_key="+bbs; 
				}
			}
		} 

		function prompt_action_thread(th, bbs, host) {
			jPrompt("イラスト投稿時に入力した削除キーを入力して下さい","","削除のための削除キーの入力",function(key){
				if (key){
					location.href = ""+host+"del_thread?thread_key="+th+"&bbs_key="+bbs+"&del_key="+key;
				}
			});
		} 

		function prompt_action_thread_edit(th, bbs) {
			jPrompt("イラスト投稿時に入力した削除キーを入力して下さい","","編集のための削除キーの入力",function(key){
				if (key){
					location.href = ""+host+"draw_moper?thread_key="+th+"&bbs_key="+bbs+"&del_key="+key;
				}
			});
		} 

		function open_draw(url,reply_mode,host,thread_key,bbs_key,illust_mode){
			var width=400;
			var height=400;
			if(reply_mode){
				width=document.getElementById("canvas_width_"+thread_key).value;
				height=document.getElementById("canvas_height_"+thread_key).value;
			}
			var is_ipad="";
			if(!isFlashInstalled){
				is_ipad="ipad=1&";
			}
			if(reply_mode){
				if(!document.getElementById("continue_reply_"+thread_key)){
					url="";
				}else{
					if(!document.getElementById("continue_reply_"+thread_key).checked){
						url="";
					}
				}
			}
			if(illust_mode==2 && !reply_mode){
				window.location.href=''+host+'draw_moper?thread_key='+thread_key+'&bbs_key='+bbs_key+'&canvas_url='+url;
			}else{
				window.location.href=''+host+'draw?'+is_ipad+'thread_key='+thread_key+'&bbs_key='+bbs_key+'&canvas_width='+width+"&canvas_height="+height+"&canvas_url="+url+"&reply="+reply_mode;
			}
		}
		
		function show(inputData) {
			var objID=document.getElementById( "layer_" + inputData );
			var buttonID=document.getElementById( "category_" + inputData );
			if(objID.className=='close') {
				objID.style.display='block';
				objID.className='open';
			}else{
				objID.style.display='none';
				objID.className='close';
			}
		}
		
		function AddBookmark(host,thread_key){
			jPrompt("このイラストをブックマークしますか？<BR>以下のフォームからブックマークにコメントを付加することもできます。","","ブックマーク",
				function(comment){
					if(comment==null){
						return;
					}
					window.location.href=host+'add_bookmark?mode=add&thread_key='+thread_key+'&comment='+comment;
				}
			);
		}
		
		function show_comment_form(id){
			document.getElementById('comment_form_'+id).style.display='block';
			document.getElementById('comment_form_button_'+id).style.display='none';
		}

		function show_tag_form(id){
			document.getElementById('tag_form_'+id).style.display='block';
			document.getElementById('tag_form_button_'+id).style.display='none';
		}

		function display_comment_tab(type,thread_key){
			if($(".comment_tab_"+thread_key+"_"+type).hasClass("checked")){
				$(".comment_tab_"+thread_key).removeClass("checked");
				$(".comment_tab_"+thread_key+"_body").hide();
				return;
			}

			$(".comment_tab_"+thread_key).removeClass("checked");
			$(".comment_tab_"+thread_key+"_"+type).addClass("checked");

			$(".comment_tab_"+thread_key+"_body").hide();
			$(".comment_tab_"+thread_key+"_body_"+type).show();
		}

		function applause(host,bbs_key,thread_key,mode,order,page){
			applause_core(host,bbs_key,thread_key,mode,order,page,"");
		}

		function applause_with_comment(host,bbs_key,thread_key,mode,order,page){
			jPrompt("このイラストに拍手しますか？<BR>以下のフォームからコメントを付加することもできます。","","拍手",
				function(comment){
					if(comment==null){
						return;
					}
					applause_core(host,bbs_key,thread_key,mode,order,page,comment);
				}
			);
		}

		function applause_core(host,bbs_key,thread_key,mode,order,page,comment){
			var url=host+'applause?bbs_key='+bbs_key+'&amp;thread_key='+thread_key+'&amp;mode='+mode;
			if(mode=="bbs"){
				url+="&amp;order="+order+"&amp;page="+page
			}
			if(comment!=""){
				url+="&amp;comment="+comment
			}
			window.location.href=url
		}
