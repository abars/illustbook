//--------------------------------------------------------
//スレッドスクリプト
//copyright 2010-2012 ABARS all rights reserved.
//--------------------------------------------------------

		function select_change(order_value,url_base,page){
			var order=order_value;
			window.location.href=''+url_base+page+"&order="+order;
		}

		function confirm_action(url) {
			if (confirm("本当に削除しますか?")){
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
			var key=prompt("イラスト投稿時に入力した削除キーを入力して下さい","");
			if (key){
				location.href = ""+host+"del_thread?thread_key="+th+"&bbs_key="+bbs+"&del_key="+key;
			}
		} 

		function prompt_action_thread_edit(th, bbs) {
			var key=prompt("イラスト投稿時に入力した削除キーを入力して下さい","");
			if (key){
				location.href = ""+host+"draw_moper?thread_key="+th+"&bbs_key="+bbs+"&del_key="+key;
			}
		} 

		function open_draw(url,reply_mode,host,thread_key,bbs_key,illust_mode){
			var width=400;
			var height=400;
			if(reply_mode){
				width=document.getElementById("canvas_width").value;
				height=document.getElementById("canvas_height").value;
			}
			if(illust_mode==2 && !reply_mode){
				window.location.href=''+host+'draw_moper?thread_key='+thread_key+'&bbs_key='+bbs_key+'&canvas_url='+url;
			}else{
				window.location.href=''+host+'draw?thread_key='+thread_key+'&bbs_key='+bbs_key+'&canvas_width='+width+"&canvas_height="+height+"&canvas_url="+url+"&reply="+reply_mode;
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