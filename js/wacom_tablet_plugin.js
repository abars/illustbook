	//================================================
	//WacomTabletPluginを使用する
	//================================================

	var WACOM_PLUGIN_CHECK_INTERVAL=1000;

	var m_wacom_plugin=null;
	var m_plugin_load_finish=false;
	var m_notify_text="";
	
	//================================================
	//プラグインの読み込み
	//================================================

	//まずプラグインを読み込みに行く
	function initWacom(){
		//サポートしていないブラウザではプラグインを読み込まない
		//最新のプラグインがリリースされた場合はisSupportBrowser()の中でverチェックするので以下をコメントアウトのこと
		if(!isSupportBrowser()){
			m_plugin_load_finish=true;
			return;
		}

		//プラグインを有効化(display:noneはIEで使えない)
		var text="<!--[if IE]><object id='Wacom' classid='CLSID:449E4080-7C69-4767-A1AE-6AAE25B0B906' codebase='http://www.wacom.com/U/plugins/Windows/WacomIE.cab#Version=-1,-1,-1,-1'></object><![endif]--><!--[if !IE]><--><embed name='wacom-plugin' id='wacom-plugin' type='application/x-wacom-tablet' HIDDEN='TRUE' pluginspage='http://www.wacom.com/productsupport/plugin.php'></embed><!--><![endif]-->";
		document.getElementById("wacomPlugin").innerHTML=text;
		checkWacom();
	}

	function checkWacom(){
		//Pluginを取得
		m_wacom_plugin=(window.Wacom || document.embeds["wacom-plugin"]);
		
		//まだロードが完了していなかったらもう一度探しに行く
		if(!(m_wacom_plugin.version)){
			setTimeout("checkWacom()",WACOM_PLUGIN_CHECK_INTERVAL);
			return;
		}
		
		//読み込み完了
		m_plugin_load_finish=true;
	}
	
	function isPluginLoadFinish(){
		return m_plugin_load_finish;
	}

	//================================================
	//筆圧をサポートしているか判定する
	//================================================

	function isSupportBrowser(){
		//最新のWacomTabletPluginがリリースされたら下記を有効化
	
		//Windowsであれば最新のプラグインであれば問題無い
		//if(checkIsRatestPlugin() && isWindows()){
		//	return true;
		//}

		//そうでなければIEとSafariだけでしか動作しない
		var ver = window.opera ? (opera.version().replace(/\d$/, "") - 0):parseFloat((/(?:IE |fox\/|ome\/|ion\/)(\d+\.\d)/.exec(navigator.userAgent)||[,0])[1]);
		if (navigator.userAgent.indexOf("Chrome") > -1){
			return false;	//Chromeはサポートしない
		}
		if (navigator.userAgent.indexOf("Safari") > -1){
			return true;	//Safariはサポートする
		}
		if(navigator.userAgent.indexOf("MSIE") > -1){
			if(ver>=9)
				return false;	//IE9以降はサポートしない
			return true;	//IE8まではサポートする
		}
		if (navigator.userAgent.indexOf("Opera") > -1){
			return true;	//Operaはサポートする
		}
		if(navigator.userAgent.indexOf("Firefox") > -1){
			var limit=3.7;	//Macの場合は3.6まで
			if(navigator.userAgent.match("Windows")){
				limit=3.6;	//Windowsの場合は3.5まで
			}
			if(Number(ver)<limit)
				return true;
			return false;	//3.6と4.0はサポートしない
		}
  		return true;
	}
	
	//サポートしていなかった場合にFlash上に表示されるメッセージを取得する
	function getNotifyText(){
		return m_notify_text;
	}
	
	//================================================
	//最新版のプラグインを使用しているか確認する
	//================================================

	function isIe(){
		if (navigator.userAgent.indexOf("Chrome") > -1){
			return false;
		}
		if (navigator.userAgent.indexOf("Safari") > -1){
			return false;
		}
		if(navigator.userAgent.indexOf("MSIE") > -1){
			return true;
		}
		return false;
	}
	
	function isWindows(){
		return (navigator.userAgent.indexOf("Win") != -1);
	}
	
	function getWacomPluginVersion(){
		var obj=new Object();
		var ver=""+m_wacom_plugin.version;
		obj.major=Number(ver.charAt(0));
		obj.minur1=Number(ver.charAt(1));
		obj.minur2=Number(ver.charAt(2));
		obj.minur3=Number(ver.charAt(3));
		if(ver.charAt(4)){
			obj.minur3=obj.minur3*10+Number(ver.charAt(4));
		}
		return obj;
	}
	
	function getWacomRequireVersion(){
		if(isWindows()){
			if(isIe()){
				//ieはver1.1.0.12がある
				//それ以下の場合はIE9で動かない
				return 12;
			}

			//nsの場合はver1.1.0.10がある
			//それ以下の場合はChromeで動かない
			return 10;
		}
		
		//macはver1.1.0.1しか無い
		//どのみちChromeで動かない
		return 1;
	}
	
	function checkIsRatestPlugin(){
		var require=getWacomRequireVersion();
		
		var obj=getWacomPluginVersion();
		if(obj.major>=1 && obj.minur1>=1 && obj.minur2>=0 && obj.minur3>=require){
			return true;
		}
		
		m_notify_text="最新のタブレットプラグインをインストールして下さい。　";
		m_notify_text+="使用中："+obj.major+"."+obj.minur1+"."+obj.minur2+"."+obj.minur3+"　";
		m_notify_text+="最新版：1.1.0."+require+"\n";
		return false;
	}
	
	//================================================
	//筆圧の取得
	//================================================
	
	function getPressure(){
		if(!isPen())
			return 1.0;//0.5;
		return m_wacom_plugin.pressure;
	}
	
	function isPen(){
		if(!m_wacom_plugin)
			return false;
		if(!m_wacom_plugin.isWacom)
			return false;
		var pointer_type=m_wacom_plugin.pointerType;
		if(pointer_type==1 || pointer_type==3)	// 1==Pen 3==Eraser
			return true;
		return false;
	}
	
	function isEraser(){
		if(!m_wacom_plugin)
			return 0;
		if(!m_wacom_plugin.isWacom)
			return 0;
		return m_wacom_plugin.isEraser;
	}
	
