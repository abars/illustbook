//--------------------------------------------------------
//スレッドスクリプト
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

var isFlashInstalled=function(){if(navigator.plugins["Shockwave Flash"]){return true;}try{new ActiveXObject("ShockwaveFlash.ShockwaveFlash");return true;}catch(a){return false;}}();

		function select_change(order_value,url_base,page,limit){
			var order=order_value;
			window.location.href=''+url_base+page+"&order="+order+"&limit="+limit;
		}

		function confirm_action_comment(url,is_english) {
			var msg="本当にコメントを削除しますか?";
			if(is_english){
				msg="Are you sure you want to delete this comment?"			
			}
			if (confirm(msg)){
				location.href = url; 
			}
		}

		function confirm_action_term(url,is_english) {
			var msg="本当に規約設定を変更しますか?";
			if(is_english){
				msg="Are you sure you want to set violate terms?"			
			}
			if (confirm(msg)){
				location.href = url; 
			}
		}

		function confirm_action_thread(th, bbs, host ,is_english) {
			var msg="本当に削除しますか?";
			if(is_english){
				msg="Are you sure you want to delete this illust?"			
			}
			if (confirm(msg)){
				msg="削除したデータは復元できません。本当に削除しますか?";
				if(is_english){
					msg="This operation cannot be undone.Are you sure you want to delete this illust?"
				}
				if (confirm(msg)){
					location.href = ""+host+"del_thread?thread_key="+th+"&bbs_key="+bbs; 
				}
			}
		} 

		function prompt_action_thread(th, bbs, host, is_english) {
			var msg="削除するためにイラスト投稿時に入力した削除キーを入力して下さい";
			var title="削除のための削除キーの入力";
			if(is_english){
				msg="Please set delete key of illust"			
				title="Input delete key for Delete"
			}
			jPrompt(msg,"",title,function(key){
				if (key){
					location.href = ""+host+"del_thread?thread_key="+th+"&bbs_key="+bbs+"&del_key="+key;
				}
			});
		} 

		function prompt_action_thread_edit(th, bbs, is_english) {
			var msg="編集するためにイラスト投稿時に入力した削除キーを入力して下さい";
			var title="編集のための削除キーの入力";
			if(is_english){
				msg="Please set delete key of illust"			
				title="Input delete key for Edit"
			}
			jPrompt(msg,"",title,function(key){
				if (key){
					location.href = ""+host+"draw_moper?thread_key="+th+"&bbs_key="+bbs+"&del_key="+key;
				}
			});
		} 

		function open_draw(url,reply_mode,host,entry_key,thread_key,bbs_key,illust_mode){
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
			if(reply_mode && entry_key==""){
				if(!document.getElementById("continue_reply_"+thread_key)){
					url="";
				}else{
					if(!document.getElementById("continue_reply_"+thread_key).checked){
						url="";
					}
				}
			}
			var url2="";
			if(illust_mode==2 && !reply_mode){
				url2=''+host+'draw_moper?thread_key='+thread_key+'&bbs_key='+bbs_key+'&canvas_url='+url;
			}else{
				url2=''+host+'draw?'+is_ipad+'entry_key='+entry_key+'&thread_key='+thread_key+'&bbs_key='+bbs_key+'&canvas_width='+width+"&canvas_height="+height+"&canvas_url="+url+"&reply="+reply_mode;
			}
			if(is_ipad!=""){
				window.open(url2,false);
			}else{
				window.location.href=url2;
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
		
		function AddBookmark(host,thread_key,is_english){
			var msg=is_english ? "Add this illust to your bookmark? You can also add comment from this form.":"このイラストをブックマークしますか？<BR>以下のフォームからブックマークにコメントを付加することもできます。";
			var title=is_english ? "Bookmark":"ブックマーク";
			jPrompt(msg,"",title,
				function(comment){
					if(comment==null){
						return;
					}
					comment=encodeURI(comment);
					url=host+'add_bookmark?mode=add&thread_key='+thread_key+'&comment='+comment;

					msg=is_english ? "processing":"ブックマークしています。";
					jAlert(msg,title);
					$('#popup_ok').hide();

					//window.location.href=url;

					$.get(url, function(data){
						var msg=is_english ? "success":"ブックマークに成功しました。";
						jAlert(msg,title);
					});
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

		var g_request_thread_key="";
		var g_remote_host="";

		function get_host(remote_host){
			g_remote_host=remote_host;
			document.getElementById("remote_host_"+g_request_thread_key).value=remote_host;
		}

		function request_host(thread_key){
			g_request_thread_key=thread_key;
			if(g_remote_host!=""){
				get_host(g_remote_host);
				return;
			}
			var script = document.createElement('script');
			script.src = 'http://www.abars.biz/remote_host/remote_host.php?callback=get_host';
			document.body.appendChild(script);
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

			request_host(thread_key)
		}

		function applause(host,bbs_key,thread_key,mode,order,page){
			applause_core(host,bbs_key,thread_key,mode,order,page,"","",false);
		}

		function applause_with_comment(host,bbs_key,thread_key,mode,order,page,is_english){
			var msg="このイラストに拍手しますか？<BR>以下のフォームからコメントを付加することもできます。";
			var title="拍手";
			if(is_english){
				msg="Does you like this illust? You can also add comment from this form.";
				title="Like with comment";
			}
			jPrompt(msg,"",title,
				function(comment){
					if(comment==null){
						return;
					}
					applause_core(host,bbs_key,thread_key,mode,order,page,comment,title,is_english);
				}
			);
		}

		var applause_finish=new Object();

		function applause_core(host,bbs_key,thread_key,mode,order,page,comment,title,is_english){
			if(applause_finish[thread_key] && comment==""){
				return;
			}

			//カウントアップ
			var count_div=$("#applause_value_"+thread_key);
			var count=Number(count_div.html());
			count++;
			count_div.hide().html(count).fadeIn(500);
			applause_finish[thread_key]=true;

			//リクエストを送る
			var url=host+'applause?bbs_key='+bbs_key+'&amp;thread_key='+thread_key+'&amp;mode='+mode;
			if(mode=="bbs"){
				url+="&amp;order="+order+"&amp;page="+page
			}
			if(comment!=""){
				url+="&amp;comment="+comment
			}

			//コメント付き拍手はページ遷移、そうでなければ非同期
			if(comment==""){
				//window.location.href=url
				//非同期
			}else{
				//同期
				msg=is_english ? "processing":"拍手しています。";
				jAlert(msg,title);
				$('#popup_ok').hide();

				$.get(url, function(data){
					var msg=is_english ? "success":"拍手に成功しました。";
					jAlert(msg,title,function(){
						window.location.href=url
					});
				});
			}
		}
