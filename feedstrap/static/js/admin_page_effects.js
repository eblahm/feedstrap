function feed_save() {

    var owner = $("#feed_owner").val();
    var office = $("#feed_office").val();
    var url = encodeURIComponent($("#feed_url").val());
    var f_description = $("#feed_description").val();
    var f_origin = $("#feed_origin").val();
    var f_format = $("#feed_format").val();
    var f_issue = $("#feed_issue").val();
    var f_policy = $("#feed_policy").val();
    var c = $("#feed_pass").val();

    var dataString = "owner=" + owner + "&office=" + office + "&url=" + url + "&description=" + f_description + "&f_origin=" + f_origin + "&f_format=" + f_format + "&f_issue=" + f_issue + "&f_policy=" + f_policy + "&c=" + c;
    $.ajax({
        url: "/addfeed",
        data: dataString,
        dataType: "html",
        success: function (data) {
            $("#add_response").html(data);


            if (data == "Your feed was successfully added! New items from this feed will input automatically into the database") {
                $("#feed_save_button").hide();
                $.ajax({
                    url: "/repostfeed",
                    data: dataString,
                    dataType: "html",
                    success: function (data) {
                        $(".feeds_table").append(data);
                    }
                });
            } else {
                return false
            }

        }
    });

};
function getselectors() {
          $.ajax({
                url: "/gs",
                dataType: "html",
                success: (function (data) {
                  $("#selector_textareas").html(data);

                })
            })
          }
          
 function getdbtools() {
 
$("#tools_content").html('<div class="centered" style="padding:50px;"><img src="/img/loader.gif" /></div>')
          $.ajax({
                url: "/gpt",
                dataType: "html",
                success: (function (data) {
                  $("#tools_content").html(data);
        var at = $( "#pt_change_to_value" ).attr("name");
        var at_decode = at.replace(/%%/g, ' ');
        at_decode = at_decode.replace(/##/g, '/');
        var availableTags = at_decode.split(",");
        $( "#pt_change_to_value" ).autocomplete({
            source: availableTags
        });
   

                })
            })
   }

function cpt() {
  var cfrom = $("#pt_change_from_value").val();
  var cto = $("#pt_change_to_value").val();
  var dataString = "cfrom="+cfrom+"&cto="+cto;
  var cfrom_length = String(cfrom.length)
  var confirm_message = "Are you sure you want to change the selected(" + cfrom_length + ') records policy to "' + cto + '"?';
  if (confirm(confirm_message)) {
          $.ajax({
                url: "/cpt",
                type: "POST",
                data: dataString,
                dataType: "html",
                success: (function (data) {
                  $("#pt_message").html(data);

                })
            })
           }
         
}




$(document).ready(function () {
  
    $(".modTrigger2").live("click", function (event) {
        var ref = $(this).attr('name');

        $.ajax({
            url: ref,
            dataType: "html",
            success: function (data) {
                $('#mod_content2').html(data);
                $('#mod_content2').jqm({
                    modal: true,
                    // onHide: modcloser,
                });
                $('#mod_content2').jqmShow();
            }
        });
    });

    $(".tab").click(function () {
        var this_content_box = $(this).attr('name');        
        $(".tab").toggleClass("mytab_selected", false);
        $(".tab").toggleClass("mytab_unselected", true);
        $(this).toggleClass("mytab_unselected", false);
        $(this).toggleClass("mytab_selected", true);
  
        $(".content_div").hide();
        $("#"+this_content_box).show();
    });


    $("#delete_selected_feed").click(function () {

        var c = $("#dpass").val();
        var node_list = document.getElementsByTagName("input");
        var ids = new Array;
        for (var i = 0; i < node_list.length; i++) {
            var node = node_list[i];
            if (node.checked == true) {
                // do something here with a <input type="text" .../>
                // we alert its value here
                var ID = node.getAttribute('id');
                ids.push(ID)
            }
        }

        var confirm_message = "Are you sure you want to delete the selected feed(s)?"
        if (confirm(confirm_message)) {

            var dataString = "ids=" + ids + "&c=" + c
            $.ajax({
                url: "/deletefeed",
                data: dataString,
                dataType: "html",
                success: (function (data) {
                    for (var i = 0; i < ids.length; i++) {
                        var node = ids[i];
                        $("#row_" + node).hide()
                    }


                })
            })
        } else {
            return false
        }
    });

    $("#add_feed").click(function () {

        $("#add_f_row").show();
        $("#add_f_submit").show();


    })
      
   $(".save_changes").live("click", function (event) { 
    var selector = $(this).attr('id');
    $("#save_response_"+ selector).html('<img src="/img/loader_bar.gif" />')
    var ref = $(this).attr('name');  
    var new_categories = $("#"+ref).val();
    new_categories = new_categories.replace(/\n\r?/g, '|');
    var dataString = "selector=" + selector + "&content=" + new_categories;
    var ct = new Date();
    var hours = ct.getHours();
    if (hours < 10){
        hours = "0" + hours
       };
    var minutes = ct.getMinutes();
    if (minutes < 10){
        minutes = "0" + minutes
       };
    var seconds = ct.getSeconds();
    if (seconds < 10){
        seconds = "0" + seconds
       };
    var t = hours + ":" + minutes + ":" + seconds;
    if (seconds < 10){
        seconds = "0" + seconds
       };

    $.ajax({
        url: "/selector_change",
        type: "POST",
        data: dataString,
        dataType: "html",
        error: function() { $("#save_response_"+ selector).html("SAVE FAILED, Try Again") },
        success: function (data) {
           
           $("#save_response_"+ selector).html("<em>Updated at " + t +"</em>");
           

        }
    });


    })

   $("#tab_db_tools").live("click", function (event) {
   getdbtools();
   });
          
   $(".resel").live("click", function (event) { 
    var selector = $(this).attr('name');
    $("#save_response_"+ selector).html('<img src="/img/loader_bar.gif" />')
    var dataString = "selector=" + selector;
    var ct = new Date();
    var hours = ct.getHours();
    if (hours < 10){
        hours = "0" + hours
       };
    var minutes = ct.getMinutes();
    if (minutes < 10){
        minutes = "0" + minutes
       };
    var seconds = ct.getSeconds();
    if (seconds < 10){
        seconds = "0" + seconds
       };
    var t = hours + ":" + minutes + ":" + seconds;
    $.ajax({
        url: "/resel",
        type: "GET",
        data: dataString,
        dataType: "html",
        error: function() { $("#save_response_"+ selector).html("REPOPULATED FAILED") },
        success: function (data) {
          
          $.ajax({
                url: "/gs",
                dataType: "html",
                error: function() { $("#save_response_"+ selector).html("REPOPULATED FAILED") },
                success: (function (data) {
                  $("#selector_textareas").html(data);
                  $("#save_response_"+ selector).html("REPOPULATED at " + t);
                })
            })
            
        }
    });


    })

   $("#ocap").live("click", function (event) {
       $("#save_response_ocap").html('<img src="/img/loader_bar.gif" />')
       var new_categories = $("#other_capabilities").val();
       new_categories = new_categories.replace(/\n\r?/g, '|');
       var dataString = "content=" + new_categories;
       var ct = new Date();
       var hours = ct.getHours();
       if (hours < 10) {
           hours = "0" + hours
       };
       var minutes = ct.getMinutes();
       if (minutes < 10) {
           minutes = "0" + minutes
       };
       var seconds = ct.getSeconds();
       if (seconds < 10) {
           seconds = "0" + seconds
       };
       var t = hours + ":" + minutes + ":" + seconds;
   $.ajax({
        url: "/ocap",
        type: "POST",
        data: dataString,
        dataType: "html",
        error: function() { $("#save_response_ocap").html("SAVE FAILED, Try Again") },
        success: function (data) {           
           $("#save_response_ocap").html("<em>Updated at " + t +"</em>");
        }
    });

   })

 getselectors();

});