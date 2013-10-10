



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
            var additional_peram = $.mustache($('#filter_widget').html(), {'filter_count': filter_count});

            $("#additional_perams").append(additional_peram);

            $(function() {
                $("#fv"+filter_count).autocomplete({source: all_tags.getData()});
            });
        });

        $("#advanced_search").on("change", ".field_selector", function (event) {
            var filter_count = $(this).data('filter_count');
            var widget = $('[name="' + $(this).val() +'"]').clone().attr({id: null});
            var this_ui = widget.data('ui');

            widget.attr({name: filter_count + '_' + widget.attr('name')}).addClass("primary_filter");
            $("#"+filter_count+"_value").html(widget);

            var ui_options = {
                datepicker: function() {
                widget.datepicker();
                widget.datepicker( "option", "dateFormat", 'yy-mm-dd' );
                },
                tags_autocomplete: function() {
                    $(function() {widget.autocomplete({source: all_tags.getData()});});
                }
            };

            ui_options[this_ui]();
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
