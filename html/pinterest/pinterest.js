<script type="text/javascript">
/* for w3c validater */
/* <![CDATA[ */

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

/* ]]> */
</script>
