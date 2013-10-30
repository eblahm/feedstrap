



require(["/static/js/feedstrap/utils.js"], function(utils) {
    $(document).ready(function () {

        var ui_options = {
            datepicker: function(selected) {
                var currentval = selected.val();
                selected.datepicker();
                selected.datepicker( "option", "dateFormat", 'yy-mm-dd' );
                selected.val(currentval);
            },
            tags_autocomplete: function(selected) {
                $(function() {selected.autocomplete({source: all_tags.getData()});});
            },
            apply: function(selected) {
                if(!(selected.data('ui') == undefined)) {
                    this[selected.data('ui')](selected)
                };
            }
        };

        function drop_in_filter(existing_count){
            var additional_peram = $.mustache($('#mustache_template').html(),
                {
                    'filter_count': existing_count,
                    'c': 'primary_filter'
                });
            if (existing_count > 1) {
                $("#advanced_search").append(additional_peram);
            }
            else {
                $("#advanced_search").html(additional_peram);
            }

            var new_filter = $('.primary_filter').last();
            ui_options.apply(new_filter);
        }

        $('#advanced_search_modal').on('shown', function () {
            $('.primary_filter').each(function(){
                ui_options.apply($(this));
            });
            $($('.primary_filter')[0]).focus();
        })


        $("#add_new_filter").click(function (event){
            var filter_count =  parseInt($('.field_selector').last().data('filter_count'), 10) + 1;
            drop_in_filter(filter_count)
        });

        $("#reset").click(function (event){
            drop_in_filter(1);
            $('.a_o').last().html('')
        });

        $("#advanced_search").on("change", ".field_selector", function (event) {
            var filter_count = $(this).data('filter_count');
            var widget = $('[name="' + $(this).val() +'"]').clone();
            var in_form_name = filter_count + '_' + widget.attr('name');
            var cell = $('#fv'+filter_count);
            cell.html(widget);

            var new_item = cell.children().first()
            new_item.addClass('primary_filter');
            new_item.attr({name: in_form_name});
            ui_options.apply(new_item);
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
            var url = "/?"+ perams;
            window.open(url, "_self");
        });

    });

});
