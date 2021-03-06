//use masonry

function masonry_reload(){
  $("#infinite-scroll-container").masonry("reload");
}

// Masonry corner stamp modifications
$.Mason.prototype.resize = function() {
  this._getColumns();
  this._reLayout();
};

$.Mason.prototype._reLayout = function( callback ) {
  var freeCols = this.cols;
  if ( this.options.cornerStampSelector ) {
    //add for treat centering
    var containerWidth = this.cols * this.columnWidth - this.options.gutterWidth;
    this.element.css({ width: containerWidth });

    //default
    var $cornerStamp = this.element.find( this.options.cornerStampSelector ),
      cornerStampX = $cornerStamp.offset().left - 
      ( this.element.offset().left + this.offset.x + parseInt($cornerStamp.css('marginLeft')) );
    freeCols = Math.floor( cornerStampX / this.columnWidth );
  }
  // reset columns
  var i = this.cols;
  this.colYs = [];
  while (i--) {
    this.colYs.push( this.offset.y );
  }

  for ( i = freeCols; i < this.cols; i++ ) {
    this.colYs[i] = this.offset.y + $cornerStamp.outerHeight(true);
  }

  // apply layout logic to all bricks
  this.layout( this.$bricks, callback );
};

function masonry_exec(){
    var $container = $('#infinite-scroll-container'); 
    $container.show();
    $container.masonry({
      itemSelector: '.item',
      isFitWidth: true,
      cornerStampSelector: '.corner-stamp'
    });

    if(!$('#index').is(':visible')){
      $('#index').width($container.width())
    }

    $('#index').show();
    $('#pinterest_footer').show();
}

$(document).ready(function(){
  var $container = $('#infinite-scroll-container'); 
  masonry_fit_image_size($container);
  masonry_exec(); //corner stampに対応
});

$( window ).resize(function(){
  masonry_exec();
});

function masonry_fit_image_size($newElems){
  var new_width=Math.floor(document.body.clientWidth/2-8);
  var LP_IPHONE_IMG_WIDTH=152;
  var finded=$newElems.find("img");

  var is_iphone=false;
  for(var i=0;i<finded.length;i++){
    if(finded[i].width==LP_IPHONE_IMG_WIDTH){ //iPhoneの場合のみ
      finded[i].height=Math.floor(new_width/finded[i].width*finded[i].height);
      finded[i].width=new_width;
      is_iphone=true;
    }
  }

  if(is_iphone){
    var finded=$newElems.find(".item");
    if(finded.length==0){
      finded=$newElems; //二周目はjQueryが扱える型ではない
    }
    for(var i=0;i<finded.length;i++){
      finded[i].style.width=""+new_width+"px";
    }
  }
}

//re layout

function show_more_tag(){
  if($('#more_tag').is(':visible')){
   $('#more_tag').hide();
   $('#show_more_tag_button').show();
  }else{
   $('#more_tag').show();
   $('#show_more_tag_button').hide();
  }
  masonry_reload();
}

function show_search(is_english){
  var search="検索";
  var close="閉じる";
  if(is_english){
    search="Search";
    close="Close";
  }
  if($('#search').is(':visible')){
    $('#search').hide();
    //$('#search_button').text(search)
  }else{
    $('#search').fadeIn();  
    //$('#search_button').text(close)
  }
  masonry_reload();
}
