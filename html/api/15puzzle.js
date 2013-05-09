//-------------------------------------------------------------------
//ブックマークしているイラストで遊べるパズルアプリ
//-------------------------------------------------------------------

//インスタンス化
var puzzle_app=new PuzzleApp();

//アプリメインクラス
function PuzzleApp(){
    //描画先
	this._canvas=null;
	
	//ゲーム
	this._tile_size=96;
	this._px=0;
	this._py=0;
	this._tile_pos=[];
	
	//ゲーム
	this._img=null;
	this._thread=null;
	
	//イラスト選択用
	this._thumbnail_list=[];
	this._thread_list=[];
	this._page=0;

	//シーン管理
	this._scene=0;
	this._SCENE_LOADING=0;
	this._SCENE_SELECT=1;
	this._SCENE_GAME=2;
    this._SCENE_CLEAR=3;
    
    //スコア
    this._start_time=0;
    this._score=0;
    this._highscore=0;
    this._new_highscore=false;
}

//illustbook.app.regist直後に呼ばれる
PuzzleApp.prototype.init=function(){
    //ログイン要求
    var current_user=illustbook.user.getCurrentUser();
	if(current_user===""){
		alert("このアプリで遊ぶにはログインが必要です。");
		return;
	}
    
    //描画領域を確保
	this._canvas=new illustbook.canvas(this,480,480);
	
	//コールバックの登録
	this._canvas.addTouchCallback(this);	//addTouch*が呼ばれるようになる
	illustbook.app.addLoopCallback(this,1000/15);	//loopが呼ばれるようになる
	
	//描画位置
	this._px=(this._canvas.width-this._tile_size*4)/2;
	this._py=(this._canvas.height-this._tile_size*4)/2;
	
	//タイル位置
    this._tile_pos_init();
	
	//ブックマーク画像の一覧を取得する
    var limit=100;
    illustbook.bookmark.getThreadList(current_user,0,limit,illustbook.bookmark.ORDER_NONE,bookmark_callback);
    
    //ハイスコアリセット
    //this._put_highscore();
    
    //ハイスコアを取得する
    this._get_highscore();
};

//-------------------------------------------------------------------
//ハイスコア管理
//-------------------------------------------------------------------

PuzzleApp.prototype._get_highscore=function(){
    illustbook.perpetuation.getData("highscore",highscore_callback);
};

function highscore_callback(oj){
    puzzle_app._highscore_callback(oj);
}

PuzzleApp.prototype._highscore_callback=function(oj){
    if(oj.status=="failed"){
        alert("ハイスコアの取得に失敗しました。");
        return;
    }
    if(oj.status=="success"){
        this._highscore=Number(oj.response.int_data);
        return;    
    }
    if(oj.status=="nodata"){
        this._highscore=0;
        return;
    }
    alert("不明なエラー"+oj.status);
};

PuzzleApp.prototype._put_highscore=function(){
    illustbook.perpetuation.putData("highscore",this._highscore,this._score_to_string(this._highscore),put_data_callback);
};
 
function put_data_callback(oj){
    if(oj.status!="success"){
        alert("ハイスコアの送信に失敗しました。再送します。");
        this._put_highscore();
    }
}

PuzzleApp.prototype._get_now_seconds=function(){
    return Math.floor((new Date().getTime())/1000);
};

PuzzleApp.prototype._begin_score=function(){
    this._start_time=this._get_now_seconds();
};

PuzzleApp.prototype._get_now_score=function(){
    return this._get_now_seconds()-this._start_time;
};

PuzzleApp.prototype._score_to_string=function(sec){
    return ""+Math.floor(sec/60)+"分"+(sec%60)+"秒";
};

//-------------------------------------------------------------------
//タイトル画面
//-------------------------------------------------------------------

PuzzleApp.prototype._tile_pos_init=function(){
    for(var i=0;i<16;i++){
        this._tile_pos[i]=i;
    }
};

PuzzleApp.prototype._tile_sort=function(){
	var lx=3;
	var ly=3;
    var loop_cnt=100
	for(var j=0;j<loop_cnt;j++){
		var vec=Math.floor(Math.random()*4);
		switch(vec){
		case 0:vx=0;vy=-1;break;
		case 1:vx=0;vy=+1;break;
		case 2:vx=-1;vy=0;break;
		case 3:vx=+1;vy=0;break;
		}
		var tx=lx+vx;
		var ty=ly+vy;
		if(tx>=0 && tx<4 && ty>=0 && ty<4){
			this._tile_swap(ly*4+lx,ty*4+tx);
			lx=tx;
			ly=ty;
		}
	}
};

PuzzleApp.prototype._is_clear=function(){
    for(var i=0;i<15;i++){
        if(this._tile_pos[i]!=i){
            return false;
        }
    }
    return true;
};

function bookmark_callback(oj){
    puzzle_app.bookmark_callback(oj);
}

PuzzleApp.prototype.bookmark_callback=function(oj){
    oj=oj.response;

	if(oj.length===0){
		alert("ブックマーク画像が見つかりません。");
		return;
	}
	
	this._thread_list=[];
    this._thumbnail_list=[];
	for(var i=0;i<oj.length;i++){
        //使用許可の無い画像は弾く
        if(oj[i].image_url===""){
            continue;
        }
        this._thread_list.push(oj[i]);
		this._thumbnail_list.push(this._canvas.loadImage(oj[i].thumbnail_url));
	}
	
	this._scene=this._SCENE_SELECT;
};

//情報描画
PuzzleApp.prototype._draw_info=function(){
	switch(this._scene){
	case this._SCENE_LOADING:
		this._canvas.drawText("ブックマークしているイラストを読込中",0,0,12,0x000000);
		break;
	case this._SCENE_SELECT:
        this._canvas.drawText("ハイスコア："+this._score_to_string(this._highscore),0,0,12,0x000000);
		this._canvas.drawText("イラストを選択して下さい",0,0+20,12,0x000000);
        
		break;
	case this._SCENE_GAME:
        this._canvas.drawText("スコア："+this._score_to_string(this._get_now_score())+"　ハイスコア："+this._score_to_string(this._highscore),0,0,12,0x000000);
		this._canvas.drawText("イラストタイトル："+this._thread.title+"　投稿者："+this._thread.author,0,0+20,12,0x000000);
		break;
    case this._SCENE_CLEAR:
        this._canvas.drawText("クリア！",0,0,12,0x000000);
        this._canvas.drawText("スコア："+this._score_to_string(this._score),0,20,12,0x00000);
        if(this._new_highscore){
            this._canvas.drawText("ハイスコア更新！",0,40,12,0x00000);
        }
        break;
	}
    if(this._scene==this._SCENE_GAME || this._scene==this._SCENE_CLEAR){
        this._canvas.drawText("イラスト選択へ戻る",0,0+this._canvas.height-20,12,0x000000);
    }
};

//-------------------------------------------------------------------
//ゲームループ
//-------------------------------------------------------------------

PuzzleApp.prototype.loop=function(){
	this._canvas.drawBegin();
	this._canvas.fillRect(0,0,this._canvas.width,this._canvas.height,0xeeeeee);
    if(this._scene==this._SCENE_CLEAR){
        var s=this._tile_size*4;
    	var fw=this._img.width;
		var fh=this._img.height;
		var fs=fw;
		if(fw>fh){
			fs=fh;
		}        
        this._canvas.drawImageRect(this._img,0,0,fs,fs,this._px,this._py,s,s);
    }else{
    	for(var y=0;y<4;y++){
    		for(var x=0;x<4;x++){
    			var no=y*4+x;
    			this._draw_one_tile(x,y,no);
    		}
    	}
    }
	this._draw_info();
	this._canvas.drawEnd();
};

PuzzleApp.prototype._draw_one_tile=function(x,y,no){
	var ts=this._tile_size-2;
	var tx=this._px+x*this._tile_size;
	var ty=this._py+y*this._tile_size;

	if(this._tile_pos[no]==15){
        if(this._scene==this._SCENE_SELECT){
            this._canvas.fillRect(tx,ty,ts,ts,0xffffff);
            this._canvas.drawText("NEXT",tx+4,ty+4,12,0x000000);
        }
		return;
    }

	if(this._scene==this._SCENE_SELECT){
		no+=this._page*15;
		if(this._thumbnail_list[no]){
			this._canvas.drawImageRect(this._thumbnail_list[no],0,0,100,100,tx,ty,ts,ts);
		}
		return;
	}

	this._canvas.fillRect(tx,ty,ts,ts,0xffffff);

	if(this._scene==this._SCENE_GAME){
        if(this._img){
		    var fw=this._img.width/4;
		    var fh=this._img.height/4;
		    var fs=fw;
		    if(fw>fh){
			    fs=fh;
		    }
	    	var fx=(this._tile_pos[no]%4)*fs;
		    var fy=Math.floor(this._tile_pos[no]/4)*fs;
		    this._canvas.drawImageRect(this._img,fx,fy,fs,fs,tx,ty,ts,ts);
        }else{
            this._begin_score();    //絵が読込まれるまでスコアを更新しない
        }
	}
};

PuzzleApp.prototype._get_tile_no=function(x,y){
	x-=this._px;
	y-=this._py;
	x/=this._tile_size;
	y/=this._tile_size;
    if(x<0 || x>=4) return -1;
    if(y<0 || y>=4) return -1;
	return Math.floor(y)*4+Math.floor(x);
};

PuzzleApp.prototype._tile_swap=function(i,j){
	var tmp=this._tile_pos[i];
	this._tile_pos[i]=this._tile_pos[j];
	this._tile_pos[j]=tmp;
};

PuzzleApp.prototype._go_game=function(no){
	if(no==15){
		this._page++;
		if(this._page*15>=this._thread_list.length){
			this._page=0;
		}
		return;
	}
	no+=this._page*15;
	this._thread=this._thread_list[no];
	if(this._thread===null)
		return;
	this._img=this._canvas.loadImage(this._thread.image_url);
	this._scene=this._SCENE_GAME;
    this._begin_score();
	this._tile_sort();
};

PuzzleApp.prototype._go_clear=function(){
    this._scene=this._SCENE_CLEAR;
    this._score=this._get_now_score();    
    this._new_highscore=false;
    if(true){//}this._score<this._highscore || this._highscore==0){
        this._highscore=this._score;
        this._new_highscore=true;
        this._put_highscore();
    }
};

//-------------------------------------------------------------------
//イベント管理
//-------------------------------------------------------------------

//タッチされたか、マウスでクリックされた
PuzzleApp.prototype.onTouchStart=function(x,y){
    if(this._scene==this._SCENE_GAME || this._scene==this._SCENE_CLEAR){
        if(y>=this._canvas.height-20 && x<100){
			this._scene=this._SCENE_SELECT;
            this._tile_pos_init();
            return;
        }
    }
    var no=this._get_tile_no(x,y);
	switch(this._scene){
	case this._SCENE_LOADING:
		break;
	case this._SCENE_SELECT:
        if(no==-1)
            return;
		this._go_game(no);
		break;
	case this._SCENE_GAME:
        if(no==-1){
            return;
        }
		if(no%4>=1 && this._tile_pos[no-1]==15){ this._tile_swap(no-1,no); }
		if(no%4<=2 && this._tile_pos[no+1]==15){ this._tile_swap(no+1,no); }
		if(Math.floor(no/4)>=1 && this._tile_pos[no-4]==15){ this._tile_swap(no-4,no); }
		if(Math.floor(no/4)<=2 && this._tile_pos[no+4]==15){ this._tile_swap(no+4,no); }
        if(this._is_clear()){
            this._go_clear();
        }
		break;
	}
};

//タッチしながら移動されたか、マウスが移動した(ドラッグ中で無くても呼ばれる)
PuzzleApp.prototype.onTouchMove=function(x,y){
};

//タッチが終了されたか、マウスを離した
PuzzleApp.prototype.onTouchEnd=function(){
};

//イラストブックにアプリを登録する
illustbook.app.regist(puzzle_app);
