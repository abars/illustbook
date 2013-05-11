<script type="text/javascript">
/* for w3c validater */
/* <![CDATA[ */

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
    var $cornerStamp = this.element.find( this.options.cornerStampSelector ),
      cornerStampX = $cornerStamp.offset().left - 
      ( this.element.offset().left + this.offset.x + parseInt($cornerStamp.css('marginLeft')) );
      //alert(""+cornerStampX+"/"+this.columnWidth);
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
    $('#index').width($container.width())
    $('#index').show();
    $('#pinterest_footer').show();
}

$(document).ready(function(){
  masonry_exec(); //windowの確定
  masonry_exec(); //corner stampに対応
});

$( window ).resize(function(){
  masonry_exec();
});


/* ]]> */
</script>
