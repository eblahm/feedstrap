
function searchrun() {
  $("#bulk_viewer").hide();
  $("#loader_gif").show();
  $("#loader_gif").html('<img src="/img/loader.gif" />')
  
  var origin = $("#origin_filter").val();
  var format = $("#format_filter").val();
  var office = $("#office_filter").val();
    var date_from = $("#datepicker_from").val();
    var date_to = $("#datepicker_to").val();
    var search_term = $("#search_term_input").val();
    var datastring = "search_term=" + search_term + "&date_from=" + date_from + "&date_to=" + date_to + "&format=" + format + "&origin=" + origin + "&office=" + office + "&end_num=new";
    location.href="/extend?"+datastring
//    $.ajax({
//        url: "/bulk_filter",
//        data: datastring,
//        dataType: "html",
//        error: function() { $("#loader_gif").html('<h3>YOUR SEARCH FOR "'+ search_term +'" FAILED, PLEASE TRY AGAIN</h3>');
//          },
//        success: (function (data) {
//            $("#bulk_viewer").html(data);
//      $("#loader_gif").hide();
//      $("#bulk_viewer").show();
//          recount_selectd();
//          reanimate_header();
//          recount_selectd();
//
//        })
//
//   })

}

function recount_selectd() {
  var selected_rows = $(".row_selected")
  var num_selected = String(selected_rows.length)
      if (num_selected == 1) {
  var selected_message = "There is currently " + num_selected + " selected record";
    }
  else {
  var selected_message = "There are currently " + num_selected + " selected records";
    }
     $("#currently_selected").html(selected_message);
}
function togglecboxes() {
    var cboxes = $(".bulk_cbox")
    if ($("#cbox_all").attr("checked")) {
      $(".bulk_row").toggleClass("row_selected", true);
        for (var i = 0; i < cboxes.length; i++) {
            cboxes[i].checked = true;
          recount_selectd();
        }
    } else {
      $(".bulk_row").toggleClass("row_selected", false);
        for (var i = 0; i < cboxes.length; i++) {
            cboxes[i].checked = false;
              recount_selectd();
        }

    }
}


$(".bulk_cbox").live("click", function (event) {
  var row_call = $(this).attr("name")
  if ($(this).attr("checked")) {
    $("#"+row_call).toggleClass("row_selected", true);
    recount_selectd();
  }
  else {
    $("#"+row_call).toggleClass("row_selected", false);
    recount_selectd();
  }
});



function enterpress(e) {
    if (e.keyCode == 13) {
        searchrun();
    } else {
        return false;
    }
}

function resort_bulk() {
  $("#bulk_viewer").hide();
  $("#loader_gif").show();
  $("#loader_gif").html('<img src="/img/loader.gif" />')
if ($("#resort_score").attr("selected")=="selected"){
datastring = $("#resort_score").attr("name")
}
else if ($("#resort_d_desc").attr("selected")=="selected"){
datastring = $("#resort_d_desc").attr("name")
}
else if ($("#resort_d_asc").attr("selected")=="selected"){
datastring = $("#resort_d_asc").attr("name")
}
 $.ajax({
        url: "/bulk_filter",
        data: datastring,
        dataType: "html",
        error: function() { $("#loader_gif").html('<h3>SORT FAILED</h3>');
                          $("#bulk_viewer").show();  
          },   
        success: (function (data) {
            $("#bulk_viewer").html(data);
      $("#loader_gif").hide();
      $("#bulk_viewer").show();
      reanimate_header();
      recount_selectd();
       
        })
    });
}

function my_modcloser() {
$("#editor_box").hide();
$("#jm_overwrite").toggleClass("highlighter", false);
$("#jm_append").toggleClass("highlighter", false);
$("#jm_delete").toggleClass("highlighter", false);
}
// -- date selector from --
$(function () {
    $("#datepicker_from").datepicker();
    $("#format").change(function () {
        $("#datepicker").datepicker("option", "dateFormat", $(this).val());
    });
});
// -- date selector to --
$(function () {
    $("#datepicker_to").datepicker();
    $("#format").change(function () {
        $("#datepicker").datepicker("option", "dateFormat", $(this).val());
    });
});

function bulk_save(edit_type) {
    var selected_items = $(".row_selected");
    var keys = '';
    for (var i = 0; i < selected_items.length; i++) {
        keys += selected_items[i].getAttribute('name') + ",";
    };
    var origin = $("#origin").val();
    var category = encodeURIComponent($("#category").val());
    var format = $("#format").val();
    var policy = encodeURIComponent($("#policy").val());
    var report = $("#report").val();
    var addtional_conditions = $("#sort_select_div").attr('name');
    var dataString = "keys=" + keys + "&origin=" + origin + "&category=" + category + "&format=" + format + "&policy=" + policy + "&report=" + report + "&" + addtional_conditions + edit_type;
    var patt = new RegExp("append|overwrite|delete");
    var et_short = patt.exec(edit_type);
    var confirm_message = "Are you sure you want to " + et_short + " the seletected records?";
    if (confirm(confirm_message)) {
      $("#bulk_viewer").hide();
      $("#loader_gif").show();
      $("#loader_gif").html('<img src="/img/loader.gif" />')
        $.ajax({
            url: "/bulk_save",
            type: "POST",
            data: dataString,
            dataType: "html",
            error: function() { $("#loader_gif").html('<h3>ERROR! SAVE FAILED, TRY AGAIN</h3>');
                          $("#bulk_viewer").show();  
             },
            success: function (data) {
                $("#loader_gif").hide();
                $("#bulk_viewer").html(data);
                $("#bulk_viewer").show();
                $("#editor_box").hide();
              reanimate_header(); 
              recount_selectd();
              
             
            }
        });
    } else {
        return false;
    }

};

$(".click_highlight").live("click", function (event) {
    var row_key = $(this).attr("name");
    var cbox = $("#cbox_"+row_key);
    var row_call = cbox.attr("name");
    if ($("#"+row_call).hasClass("row_selected")) {
        $("#"+row_call).toggleClass("row_selected", false);
        cbox.attr('checked', false);
      recount_selectd();
            }
        else {
         $("#"+row_call).toggleClass("row_selected", true);
         cbox.attr('checked', true);
          recount_selectd();
        };
});

function reanimate_header() {
  $(function() {

    var editorbox   = $("#headers"),
        page =     $(".container"),
        pageoffset = page.offset(),
        $window    = $(window),
        offset     = editorbox.offset();
        

    $window.scroll(function() {
        if ($window.scrollTop() > offset.top) { 
       editorbox.toggleClass("make_fixed", true);   
            editorbox.stop().animate({
              top: 0
            },{ duration: 1, queue: false });
        } else {
          editorbox.toggleClass("make_fixed", false); 
        }
    });
    
});
  
}
$(document).ready(function () {
  var cboxes = $(".bulk_cbox");
  $("#cbox_all").attr('checked', false);
    for (var i = 0; i < cboxes.length; i++) {
        cboxes[i].checked = false;
    }
  $("#submit_button").click(function () {
      searchrun();
    })
  
  $("#advanced_selector").click(function () {
      var av_search_box = document.getElementById("advanced_search");
      var av_toggle = document.getElementById("advanced_selector");
      if (av_search_box.style.display == "block") {
        av_search_box.style.display = "none";
        av_toggle.innerHTML = "Show Advanced...";
      } else {
        av_search_box.style.display = "block";
        av_toggle.innerHTML = "Hide Advanced...";
      }
    })
 
//  $("#loader_gif").show();
//  $("#loader_gif").html('<img src="/img/loader.gif" />')  
// $.ajax({
//        url: "/bulk_filter?search_term=office:PAS&end_num=new",
//        dataType: "html",
//        error: function() { $("#loader_gif").html('<h3>LOAD FAILED</h3>');
//          },   
//        success: (function (data) {
//            $("#bulk_viewer").html(data);
//      $("#loader_gif").hide();
//      $("#bulk_viewer").show();
 //     reanimate_header();
//      recount_selectd();
//       
//        })
//    });  
    
  
  $(".page_right").live("click", function () {
  $("#bulk_viewer").hide();
  $("#loader_gif").show();
  $("#loader_gif").html('<img src="/img/loader.gif" />');
  window.scrollTo(0, 0);
   var datastring = $(this).attr("name")
   location.href="/extend?"+datastring
//   $.ajax({
//      url: "/bulk_filter",
//      data: datastring,
//      dataType: "html",
//        error: function() { $("#loader_gif").html('<h3>PAGE RIGHT LOAD FAILED</h3>');
//                          $("#bulk_viewer").show();  
//          },
//      success: (function (data) {
//        $("#loader_gif").hide();
//        $("#bulk_viewer").html(data);
//        $("#bulk_viewer").show();
//        reanimate_header();           
//        recount_selectd();
//
//  
//      })
//  
//    })
  });
  

    $("#jm_append").live("click", function (event) {
        $(this).toggleClass("highlighter", true);
        $("#jm_delete").toggleClass("highlighter", false);
      $("#jm_overwrite").toggleClass("highlighter", false);
      
      $("#delete_button").hide();
      $("#overwrite_button").hide();
    $("#append_button").show();
    $("#editor_box").show();
    
    });
    $("#jm_delete").live("click", function (event) {
        $(this).toggleClass("highlighter", true);
      $("#jm_overwrite").toggleClass("highlighter", false);
      $("#jm_append").toggleClass("highlighter", false);
      $("#overwrite_button").hide();
    $("#append_button").hide();
      $("#delete_button").show();
    $("#editor_box").show();

    });
    $("#jm_overwrite").live("click", function (event) {
        $(this).toggleClass("highlighter", true);
        $("#jm_delete").toggleClass("highlighter", false);
      $("#jm_append").toggleClass("highlighter", false);
      
      $("#delete_button").hide();
    $("#append_button").hide();
    $("#overwrite_button").show();
    $("#editor_box").show();
    
    });
  
      $("#delete_button").live("click", function (event) {
       var edit_type = $(this).attr("name");
       bulk_save(edit_type)
    });
      $("#append_button").live("click", function (event) {
       var edit_type = $(this).attr("name");
       bulk_save(edit_type)
    });
      $("#overwrite_button").live("click", function (event) {
       var edit_type = $(this).attr("name");
       bulk_save(edit_type)
    });
  
  
      $(".details_modal").live("click", function (event) {
        var ref = $(this).attr('name');
        $.ajax({
            url: ref,
            dataType: "html",
            success: function (data) {
                $('#details_modal').html(data);
                $('#details_modal').jqm({
                    // onHide: modcloser,
                });
                $('#details_modal').jqmShow();
            }
        });
    });
    
reanimate_header()
  
});