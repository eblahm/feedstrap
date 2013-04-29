var loader_gif = '<div style="text-align:center; vertical-align: middle;"><img src="/feedstrap/static/img/loader.gif" /></div>'

function load_modal(page) {
    if (page.dbk === ""){var datastring = "";}
    else {var datastring = "k=" + page.dbk;}
    $("#modal_content").html(loader_gif);
    $.ajax({
        url: page.url,
        data: datastring,
        dataType: "html",
        error: function() { $("#modal_content").html('Load Failed :(')},
        success: (function (data) {
            $("#modal_content").html(data);
        })
    });
}

$(document).ready(function () {

    $(".expander").click(function (event){
        if ($(this).hasClass("icon-plus")){
                $("#filter").show();
                $(this).toggleClass("icon-plus", false);
                $(this).toggleClass("icon-minus", true)
            }
        else {
                $("#filter").hide();
                $(this).toggleClass("icon-minus", false);
                $(this).toggleClass("icon-plus", true);
            }
    });


    $("body").on("click", ".modal_view", function (event) {
        var dbk = $(this).data('dbk');
        var url =$(this).data('url')
        var page = {'dbk':dbk, 'url':url}
        load_modal(page);
    });

//    $("#content_view").on("click", ".read", function (event) {
//        var db_key = $(this).data('dbk');
//        load_modal(db_key, url_string="/read");
//    });
    
    $("#content_view").on("click", ".show_more", function (event) {
        var url_request = $(this).data('query');
        var content_body = $("#" + $(this).data('parent'));
        $(this).hide();
            $(".eb").html(loader_gif)
        $.ajax({
            url: url_request,
            dataType: "html",
            error: function() { content_body.append('request failed :(');},
            success: (function (data) {
                $(".eb").html("").removeClass("eb")
                content_body.append(data);
            })
        });
    });

      
    $("#modal_content").on("click", "#save_btn", function () {  
        $.ajax({
               type: "POST",
               url: "/edit/resource/",
               data: $("#popup_form").serialize(), // serializes the form's elements.
               error: function () {$("#save_status").html("error! :(")},
               success: function(data){
                   var d = jQuery.parseJSON(data);
                   $("#save_status").html(d['save_status'])
                   $("#"+d['id']).html(d['ajax_html'])
               }
               
             });
    });
    
    $("body").on("mouseenter", ".feed_item", function (event) {
        var ref = $(this).attr('id').replace("ar_", "");
        $("#article_tools_" +ref).show();
        }).on("mouseleave", ".feed_item", function (event) {
         var ref = $(this).attr('id').replace("ar_", "");
        $("#article_tools_" +ref).hide();
});

    $(".topic_row").on({
    
      click: function() {
        var k = $(this).data('k'); 
        window.location.href='/esil?k='+k;
      }
    });
    
      $(".show_des").click(function (event){
        event.stopPropagation();
        var parent = $(this).data('parent');
        var full = $(this).data('full');
        $("#" + parent).html(full);
     
     });

    $("#add_new_filter").click(function (event){
        var filter_count =  String($('.af_row').length + 1);
        var url = "/filter?a=new&filter_count=" + filter_count;
        $.ajax({
               type: "GET",
               url: url,
               success: function(data){
                   $("#advanced_search").append(data);
                   $(function() {$("#fe"+filter_count).autocomplete({source: all_tags});});
               }
        });

    });

    document.getElementById("advanced_search_form").reset();
    $(function() {$( "#fe1" ).autocomplete({source: all_tags});});
    $("#advanced_search").on("change", ".field_selector", function (event) {
        var filter_count = $(this).data('filter_count');
        var selected = $(this).val();
        var url = "/filter?a=field&filter_count=" + filter_count + "&selected=" + selected;
        $.ajax({
               type: "GET",
               url: url,
               success: function(data){
                   var new_form_element = $(data).attr({'id':"fe"+filter_count});
                   var new_name = filter_count + "_" + new_form_element.attr("name");
                   new_form_element.attr({'name': new_name}).addClass("primary_filter");
                   $("#"+filter_count+"_value").html(new_form_element);
                   if (selected == 'date_to'| selected == 'date_from') {
                       $("#fe"+filter_count).datepicker();
                       $("#fe"+filter_count).datepicker( "option", "dateFormat", 'yy-mm-dd' );
                   };
                   if (selected == 'tags') {
                       $(function() {$("#fe"+filter_count).autocomplete({source: all_tags});});
                   };
               }
        });

    })

    $("#submit_advanced_filter").click(function (event){
        var q = $(".primary_filter").serialize();
        var url = "/q?"+ q;
        window.open(url, "_self");
    });

});
