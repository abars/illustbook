

	function createHttpRequest(){
		//Win ie用
		if(window.ActiveXObject){
			try {
				//MSXML2以降用
				return new ActiveXObject("Msxml2.XMLHTTP") //[1]'
			} catch (e) {
				try {
					//旧MSXML用
					return new ActiveXObject("Microsoft.XMLHTTP") //[1]'
				} catch (e2) {
					return null
				}
			}
		} else if(window.XMLHttpRequest){
			//Win ie以外のXMLHttpRequestオブジェクト実装ブラウザ用
			return new XMLHttpRequest() //[1]'
		} else {
			return null
		}
	}

	function requestFile( data , method , fileName , async ,callback_function)
	{
		var httpoj = createHttpRequest()    
		httpoj.open( method , fileName , async )
		httpoj.onreadystatechange = function() 
		{ 
			if (httpoj.readyState==4) 
			{ 
				callback_function(httpoj)
			}
		}
		httpoj.setRequestHeader('Content-Type','application/x-www-form-urlencoded'); 
		httpoj.send( data ) 
	}
    
    var m_save_title;
    var m_save_comment;
    var m_save_name;
    var m_save_url;
    var m_save_image_key;
    var m_save_draw_time;
    var m_delete_key;
    var m_thread_key;

    var m_retry_cnt=0;
	
	function UploadComment(title,comment,name,url,image_key,draw_time,delete_key,thread_key){
        m_save_title=title;
        m_save_comment=comment;
        m_save_name=name;
        m_save_url=url;
        m_save_image_key=image_key;
        m_save_draw_time=draw_time;
        m_delete_key=delete_key;
        m_thread_key=thread_key;
        UploadCommentCore();
    }
    
    function UploadCommentCore(){    
		var data="";
		data+="mode=illust&bbs_key="+GetBbsKey()+"&";

		data+="thread_title="+encodeURI(m_save_title)+"&";
		data+="comment="+encodeURI(m_save_comment)+"&";
		data+="author="+encodeURI(m_save_name)+"&";
		data+="thread_mail="+encodeURI("")+"&";
		data+="homepage_addr="+encodeURI(m_save_url)+"&";
		data+="thread_image="+m_save_image_key+"&";
        data+="thread_key="+m_thread_key+"&";
		data+="illust_mode=2";
        data+="&draw_time="+m_save_draw_time;
        if(m_delete_key){
            data+="&delete_key="+m_delete_key;
        }

        requestFile( data , 'POST', "add_thread",true,uploadCommentFinish);
	}
	
	function uploadCommentFinish(oj){
		result=oj.responseText;
		if(result=="success"){
            window.location.href=GetHost()+"bbs_index?bbs_key="+GetBbsKey()
            return;
        }
        
        if(m_retry_cnt==0){
            m_retry_cnt++;
            UploadCommentCore();
            return;
        }
        
        alert("アップロードに失敗しました。");        
	}
