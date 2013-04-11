 


$(document).ready(function () {
function recheck(){
var boxes = $(".factor_box") 
   for (var i = 0; i < boxes.length; i++) {
   var rec = jQuery(boxes[i]);
    var this_type = rec.attr('name');
    var special_name = this_type + "_check_selected";
    if (rec.attr('checked')) {
        rec.toggleClass(special_name, true);
    } else {
        rec.toggleClass(special_name, false);
    }
   } 
    var data_sources = $(".dss_check_selected")
    var capabilities = $(".caps_check_selected")
    var options = $(".sopts_check_selected")
    var imperatives = $(".sis_check_selected")
    $('#dss_count').html(data_sources.length)
    $('#caps_count').html(capabilities.length)
    $('#sopts_count').html(options.length)
    $('#sis_count').html(imperatives.length)
}




function searchrun() {
    $("#sp_results").html('<div class="row"><div class="span8" style="text-align:center"><img src="/img/loader.gif" /></div></div>')

    var search_term = $("#search_term").val();
    var datastring = "search_term=" + search_term + "&show_line=y" + "&query_type=text";
    $.ajax({
        url: "/sp_search",
        data: datastring,
        dataType: "html",
        error: function () {
            $("#sp_results").html('<div class="row"><div class="span8" style="text-align:center"><h3>YOUR SEARCH FOR "' + search_term + '" FAILED, PLEASE TRY AGAIN</h3></div></div');
        },
        success: (function (data) {
            $("#sp_results").html(data);
            

        })

    })

};




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


      




$(document).on('keyup', function(event){
    if (event.which == 13){
        searchrun();
    };
});


$("#s_btn").on("click",  function (event) {
    searchrun();
});




$(".delete").on("click", function (event) {
  var d_url = $(this).attr('name');
  var c_key = $(this).attr('id').split("_");
  var ccode = c_key[1]
        $.ajax({
            url: d_url,
            type: "POST",
            dataType: "html",
            success: function (data) {
                $("#"+ccode).html("");
            
            }
        });
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


$(document).on("click", ".nw_link",  function (event) {
    var this_url = $(this).attr('href')    
//    window.open(this_url)
    var ajax_link = "/cl?p=sp&l=" + encodeURIComponent(this_url);
    $.ajax({
url: ajax_link, success: (function () {return false}) });
});

$(document).on("click", ".end_button",  function (event) {
    var go_to = $(this).attr('name')
    $("#sp_results").append('<div class="row ajax_load"><div class="span8" style="text-align:center"><img src="/img/loader.gif" /></div></div>')    
    $.ajax({
        url: go_to,
        dataType: "html",
        error: function () {
            $(".ajax_load").hide();
            $("#sp_results").append('<h3>SEARCH FAILED, PLEASE TRY AGAIN</h3>');
        },
        success: (function (data) {
            $(".ajax_load").hide();
            $("#sp_results").append(data);
            

        })

    })
    $(this).hide();
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



  $(document).on("click", ".live_tag",  function (event) {
    var tag = $(this).attr('name');
    var datastring = "tag=" + tag + "&show_line=y" + "&query_type=tag";
    $("#sp_results").html('<div class="row"><div class="span8" style="text-align:center"><img src="/img/loader.gif" /></div></div>');
    $.ajax({
        url: "/sp_search",
        data: datastring,
        dataType: "html",
        error: function () {
            $("#sp_results").html('<div class="row"><div class="span8" style="text-align:center"><h3>YOUR SEARCH FOR "' + search_term + '" FAILED, PLEASE TRY AGAIN</h3></div></div');
        },
        success: (function (data) {
            $("#sp_results").html(data);
        })
    })
});

  $(".show_des").click(function (event){
    event.stopPropagation();
    var rkey = $(this).attr('id');
    var full = $(this).attr('name');
    $("#des_" + rkey).html(full);
 });

 
})