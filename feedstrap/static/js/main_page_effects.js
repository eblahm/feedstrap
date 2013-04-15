
function enterpress(e) {
    if (e.keyCode == 13) {
        return false;
    } else {
        return false;
    }
}



function load_modal(db_key) {
    var datastring = "k=" + db_key;
    $("#modal_content").html('<div style="text-align:center; vertical-align: middle;"><img src="/img/loader.gif" /></div>');
    $.ajax({
        url: "db/edit/resource",
        data: datastring,
        dataType: "html",
        error: function() { $("#modal_content").html('Load Failed :(')},
        success: (function (data) {

            $("#modal_content").html(data);
        })
    });
}

function recount_selected() {
    var count = 0
    $(".row_selected").each(function (){count += 1})
    $("#num_selected").html(count)
}

$(function () {
    $("#datepicker_to").datepicker();
    $("#format").change(function () {
        $("#datepicker").datepicker("option", "dateFormat", $(this).val());
    });
});


//function adjust_table_header() {
//    var header_top_offset = $("#results_table_body").offset()['top'] - ($("#table_header_div").height()) + 5;
//    var window_position = $(window).scrollTop();
//    var nav_height = $("#my_nav").height();
//    if (window_position > header_top_offset) {
//        $("#table_header_div").css('position', 'fixed').css('top', nav_height);
//    }
//    else {
//        $("#table_header_div").css('position', '').css('top', '');
//    }
//}

//$(window).scroll( function() {
//    adjust_table_header();
//    });
    
$(function() {
    $( "#fields_list" ).sortable({
      revert: true
    });
//    $( "ul, li" ).disableSelection();
  });

$(document).ready(function () {

    $("#content_box").on("click", ".db_view", function (event) {
        var db_key = $(this).data('dbk');
        load_modal(db_key);
    });
    
    $("#content_box").on("click", ".show_more", function (event) {
        var url_request = $(this).data('query');
        var view = $(this).data('view');
        $(this).hide();      
        if (view == 'table') {
            var ajax_body = $("#results_table_body");
            $('.show_more_row').hide();
        }
        else {
            var ajax_body = $("#content_view");
        }
    $.ajax({
        url: url_request,
        dataType: "html",
        error: function() { ajax_body.append('request failed :(');},
        success: (function (data) {
            ajax_body.append(data);
        })
    });
    });
    
    $(".switch_view").click(function(event) {
        var t_btn = $("#table_switch");
        var t_box = $("#table_view");
        var l_btn = $("#list_switch");
        var l_box = $("#list_view");
    
        if ($(this).attr('id') == "list_switch"){
            l_btn.attr("disabled", true);
            l_box.show();
            $("#view_select").attr('value', 'list');
    
            t_btn.attr("disabled", false);
            t_box.hide();  }
        else {
            t_btn.attr("disabled", true);
            t_box.show();
            $("#view_select").attr('value', 'table');
            
            l_btn.attr("disabled", false);
            l_box.hide();     }
    
        });
    
//    $("#edit_btn").click( function (e) {
//       $('tool_content').toggleClass('hint--always')
//    });
      
    $("#modal_content").on("click", "#save_btn", function () {  
        $.ajax({
               type: "POST",
               url: "db/edit/resource/",
               data: $("#popup_form").serialize(), // serializes the form's elements.
               error: function () {$("#save_status").html("error! :(")},
               success: function(data){
                   var d = jQuery.parseJSON(data);
                   $("#save_status").html(d['save_status'])
                   $("#"+d['id']).html(d['ajax_html'])
               }
               
             });
    });
      
    $("#db_field_select").change(function () {
     
      var selected = $("#db_field_select option:selected").val();
      var get_url = "/ajax/get_input?f=" + selected;
    //  .each(function () {str += $(this).val()});
        $.ajax({
               type: "GET",
               url: get_url,
               error: function () {$("#bulk_holder").html("error! :(")},
               success: function(data){ $("#bulk_holder").html(data)}     
             });  
      
    });
    
    $("#select_all").click(function () {
      if ($(this).attr('checked')) {
        $(".bulk_row").toggleClass("row_selected", true);
        recount_selected();
      }
      else {
         $(".bulk_row").toggleClass("row_selected", false); 
         recount_selected();
      }
    });
    
    $("#new_fields_submit").click(function () {
      var new_fields = "new_fields=";
      $('.field_select_box[type="checkbox"]:checked').each(function(){new_fields += $(this).attr('id') + ","});
        $.ajax({
               type: "GET",
               url: "/remap_fields",
               data: new_fields,
               error: function () {$("#save_status_new_fields").html("error! :(")},
               success: function() {location.reload();}           
             });
    });
    
    $(document).on("click", ".bulk_row", function (event) { 
            $(this).toggleClass("row_selected");
            recount_selected();
    });
    
    $("#bulk_submit").click(function (){
        var dbks = "&dbks=";
        $(".row_selected").each(function (){
            dbks += $(this).attr('id')+",";
        });
        $.ajax({
               type: "POST",
               url: "/bulk_post",
               data: $("#bulk_form").serialize() + dbks, // serializes the form's elements.
               error: function () {$("#bulk_save_status").html("error! :(")},
               success: function(data){ $("#bulk_save_status").html(data);
               $(".row_selected").fadeOut().fadeIn();
               var changed_field = $(".selected_bulk").attr('name');
               var changed_value = $(".selected_bulk").val();
                $(".row_selected").each(function (){
                    var row_key = $(this).attr('id');
                    var change_cell = $("#"+changed_field+"_"+row_key);
                    change_cell.html(changed_value);
                });
               }
               
             });
    });
    
//    $(function() {$( ".table_col" ).resizable({maxHeight: 30,});});
//
//    $("#resize_save").click(function(){
//      var DataString = "";
//      var row_width = $("#sample_row").width();
//      $(".table_col").each(function(){
//          var this_ratio = String($(this).width()/row_width);
//          var this_name = $(this).attr('id').replace("_header","");
//          DataString += "col="+this_name+","+this_ratio+"&";
//      });
//      DataString += "with_ratios=yes";
//        $.ajax({
//               type: "GET",
//               url: "/remap_fields",
//               data: DataString,
//               error: function () {alert("error! :(")},
//               success: function() {location.reload();}
//             });
//    });
      
    $("#add_conditions").click(function(){
      var geturl = "/advanced_search?action=new_conditons&filter_count=" + String($(".filter").length);
      $.ajax({
                   type: "GET",
                   url: geturl,
                   error: function () {$("#all_conditions").append('<tr><td colspan="4" style="text-align:center">error! :(</td></tr>')},
                   success: function(data){
                       $("#all_conditions").append(data);
                       $(".filter_field").change(function () {ajax_input(this)});}
                 });

            });

    function ajax_input(obj) {

        var selected = $(obj).val();
        var selector_result = "#" + $(obj).attr('name') + "_result";
        var get_url = "/ajax/get_input?f=" + selected + "&filter_count="+ String($(".filter").length);
        //  .each(function () {str += $(this).val()});
        $.ajax({
            type: "GET",
            url: get_url,
            error: function () {$(selector_result).html("error! :(")},
            success: function(data){ $(selector_result).html(data)}
        });
    }

    $(".filter_field").change(function () {ajax_input(this)});

    $("#advanced_submit").click(function () {
        var dataString = 'filter_count=' + String($(".filter").length);
        $('.advanced_values').each(function(){
            var more = "&" + $(this).serialize()
            dataString += more;
        })
        $.ajax({
               type: "POST",
               url: "/advanced_search",
               data: dataString,
               error: function () {$("#advanced_status").html("error! :(")},
               success: function(data){ window.location = data}
             });     
    });

    $(".feed_item").on("mouseenter", function () {
        var ref = $(this).attr('id').replace("ar_", "");
        $("#article_tools_" +ref).show();
        }).on("mouseleave", function () {
         var ref = $(this).attr('id').replace("ar_", "");
        $("#article_tools_" +ref).hide();
});


});
