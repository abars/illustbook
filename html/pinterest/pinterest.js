<script>

// Masonry corner stamp modifications
$.Mason.prototype.resize = function() {
  this._getColumns();
  this._reLayout();
};

$.Mason.prototype._reLayout = function( callback ) {
  var freeCols = this.cols;
  if ( this.options.cornerStampSelector ) {
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

$(function(){
	
var $container = $('#container');	
	
  function masonry_exec(){
    $container.show();
    $container.masonry({
      itemSelector: '.item',
      isFitWidth: true,
      cornerStampSelector: '.corner-stamp'
    });
    $('#index').width($container.width())
    $('#index').show();
  }

masonry_exec();

$( window ).resize(function(){
  masonry_exec();
});

	$container.infinitescroll({
      navSelector  : '#page-nav',    // selector for the paged navigation 
      nextSelector : '#page-nav a',  // selector for the NEXT link (to page 2)
      itemSelector : '.item',     // selector for all items you'll retrieve
      bufferPx : 2000, // 最も下に行く前にロードをかける
      loading: {
          finishedMsg: '<div style="background-color:#ffffff;z-index:2;">ページの終端です。</div>',
          img: 'static_files/loading.gif',
          msgText: '<div style="background-color:#ffffff;z-index:2;">次のページを読込中</div>'
        }
      },
      // trigger Masonry as a callback
      function( newElements ) {
        var $newElems = $( newElements );
        $newElems.css({ opacity: 0 });
        $container.masonry( 'appended', $newElems, true ); 
        $newElems.animate({ opacity: 1 });
      }
    );
});

function masonry_reload(){
  $("#container").masonry("reload");
}

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

function show_follower(){
  if($('#follower').is(':visible')){
    $('#follower').hide();
    $('#follower_button').show();  
  }else{
    $('#follower').show();
    $('#follower_button').hide();  
  }
  masonry_reload();
}

function show_profile(){
  if($('#profile').is(':visible')){
    $('#profile').hide();
    $('#profile_button').text("詳細")
  }else{
   $('#profile').show();  
    $('#profile_button').text("閉じる")
  }
  masonry_reload();
}

function show_search(){
  if($('#search').is(':visible')){
    $('#search').hide();
    $('#search_button').text("検索")
  }else{
   $('#search').show();  
    $('#search_button').text("閉じる")
  }
  masonry_reload();
}
</script>
