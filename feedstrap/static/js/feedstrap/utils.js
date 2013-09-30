var loader_gif = '<div style="text-align:center; vertical-align: middle;"><img src="/static/img/loader.gif" /></div>';

function load_modal(page) {
    if (page.dbk === "")
        {
            var datastring = "";
        }
    else
        {
            var datastring = "k=" + page.dbk;
        };

    $("#modal_content").html(loader_gif);

    $.ajax({
        url: page.url,
        data: datastring,
        dataType: "html",
        error: (function() { $("#modal_content").html('Load Failed :(')}),
        success: (function (data)
            {
                $("#modal_content").html(data);
            })
    });
};

function enableAutoComplete(domReference, AutoCompleteArray){
    // the following code was taken from jquery ui documentation with slight style modifications

    function split(val) {
        return val.split(/,\s*/);
    };

    function extractLast(term) {
        return split(term).pop();
    }

    $(domReference)
        // don't navigate away from the field on tab when selecting an item
        .bind("keydown", function (event) {
            if (event.keyCode === $.ui.keyCode.TAB && $(this).data("ui-autocomplete").menu.active)
                {
                    event.preventDefault();
                }
        })
        .autocomplete({
            minLength: 0,
            source: (function (request, response) {
                // delegate back to autocomplete, but extract the last term
                response($.ui.autocomplete.filter(
                  AutoCompleteArray, extractLast(request.term)));
            }),
            focus: (function () {
                // prevent value inserted on focus
                return false;
            }),
            select: (function (event, ui) {
                var terms = split(this.value);
                // remove the current input
                terms.pop();
                // add the selected item
                terms.push(ui.item.value);
                // add placeholder to get the comma-and-space at the end
                // terms.push( "" );
                this.value = terms.join(", ");
                return false;
            })
        });
};

function enableSimpleAutoComplete(domReference, AutoCompleteArray) {
    $(domReference).autocomplete({
        source: AutoCompleteArray
    });
}

var all_tags = ['health care'];

(function(){
    $.ajax({
        url: '/data/tags/',
        dataType: 'json',
        success: (function(data){
            all_tags = data;
        })
    })
})();


