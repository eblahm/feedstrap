 


$(document).ready(function () {


$(document).on("click", ".submit_comment",function (event) {
    var rkey = $(this).attr('id');
    var name= $("#cname_"+rkey).val();
    var comment= $("#comment_text_"+rkey).val();
if (name==null || name=="")
  {
  alert("Name is a required field");
  return false
  }
else if (comment==null || comment=="")
  {
  alert("Comment is a required field");
  return false
  }
else {
 $("#esil_comment_"+rkey).submit();
}
});

$(".c_row").on({
  mouseover: function() {
    var rkey = $(this).attr('id');
    $("#trash_"+rkey).show();
  },
  mouseout: function() {
    var rkey = $(this).attr('id');
    $("#trash_"+rkey).hide();

  }
});


$(".comment_toggle").on("click",  function (event) {
    event.stopPropagation();
    var rkey = $(this).attr('name');
    if ($("#ctog_"+rkey).hasClass("icon-plus")){
      $("#ctog_"+rkey).toggleClass("icon-plus", false)
      $("#ctog_"+rkey).toggleClass("icon-minus", true)
      $(".comments_"+rkey).show();
    }
    else {
      $("#ctog_"+rkey).toggleClass("icon-minus", false)
      $("#ctog_"+rkey).toggleClass("icon-plus", true)
      
      $(".comments_"+rkey).hide();      
    }
});

$(".topic_row").on({

  click: function() {
    var rkey = $(this).attr('id');
   
    window.location.href='/esil/tc?rkey='+rkey;
  },
  mouseover: function() {
    var rkey = $(this).attr('id');
    $("#corner_"+rkey).css("background-color","#F5F5F5");
  },
  mouseout: function() {
    var rkey = $(this).attr('id');
    $("#corner_"+rkey).css("background-color","white");
  }
});


$(".corner").on({
  click: function() {
    var rkey = $(this).attr('name');
  
    window.location.href='/esil/tc?rkey='+rkey;
  },

  mouseover: function() {
    var rkey = $(this).attr('name');
    $("#"+rkey).css("background-color","#F5F5F5");
  },
  mouseout: function() {
    var rkey = $(this).attr('name');
    $("#"+rkey).css("background-color","white");
  }
});

  $(".show_des").click(function (event){
    event.stopPropagation();
    var rkey = $(this).attr('id');
    var full = $(this).attr('name');
    $("#des_" + rkey).html(full);
 });

 
})