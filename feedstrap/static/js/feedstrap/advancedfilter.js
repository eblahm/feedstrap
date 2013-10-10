



require(["/static/js/feedstrap/utils.js"], function(utils) {
    $(document).ready(function () {
        
        function reset_advanced_form() {
            $('#additional_perams').html('');
            document.getElementById('advanced_search_form').reset();
        };
        
        $("#as_toggle").click(function(){
            $(function() {
                $("#fe1").autocomplete({source: all_tags.getData()});
            });
        });

        $("#add_new_filter").click(function (event){
            var filter_count =  String($('.af_row').length + 1);
            var new_row = $( $('.af_row')[0]).clone();
            var new_ao = $( $('.a_o')[0]).clone();

            $("#additional_perams").append(new_ao);
            $("#additional_perams").append(new_row);
//            $(function() {
//                $("#fe"+filter_count).autocomplete({source: all_tags.getData()});
//            });
        });

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
                    if (selected == 'dateto'| selected == 'datefrom') {
                        $("#fe"+filter_count).datepicker();
                        $("#fe"+filter_count).datepicker( "option", "dateFormat", 'yy-mm-dd' );
                    };
                    if (selected == 'tags') {
                        $(function() {$("#fe"+filter_count).autocomplete({source: all_tags.getData()});});
                    };
                }
            });

        })

        $("#submit_advanced_filter").click(function (event){
            var q = $(".primary_filter");
            for (var i=0;i<q.length;i++) {
                var e = $(q[i]);
                if (e.val() == 'AND') {
                    q[i] = "";
                };
            }
            var perams = q.serialize();
            var url = "/q?"+ perams;
            window.open(url, "_self");
        });

    });

});
