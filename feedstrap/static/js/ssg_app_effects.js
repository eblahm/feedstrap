//     $(function() {
//        var at = $( "#concepts" ).attr("name");
//        var availableTags = at.split(",");
//        $( "#concepts" ).autocomplete({
//            source: availableTags
//        });
//    });
//
//     $(function() {
//        var at = $( "#tags" ).attr("name");
//        var availableTags = at.split(",");
//        $( "#tags" ).autocomplete({
//            source: availableTags
//        });
//    });
//    
//     $(function() {
//        var at = $( "#alchemy_keywords" ).attr("name");
//        var availableTags = at.split(",");
//        $( "#alchemy_keywords" ).autocomplete({
//            source: availableTags
//        });
//    });

$(document).ready(function () {

 $(".exclude").live("click", function (event) {
        var e = $(this).attr('name');
        var dbk = $(this).attr('id');
        var dataString = "e=" + e +"&dbk=" + dbk;        
        $.ajax({
            url: "/pir",
            type: "POST",
            dataType: "html",
            data: dataString,
            success: (function (data) {
            $("#"+dbk).removeClass("javascript_list");
            $("#"+dbk).removeClass("exclude");
            })
        });
        
    });

 $(".reportout").live("click", function (event) {
        var vals = $(this).attr('name')
        vals = vals.split(",");
        t = vals[0];
        fn = vals[1]; 
        var dbks = $(this).attr('id');
        var dataString = "t=" + t + "&fn=" + fn +"&dbks=" + dbks;        
        $.ajax({
            url: "/ro",
            type: "POST",
            dataType: "html",
            data: dataString,
            success: (function (data) {
            $("#my_container").html(data);
            }
)
        });
        
    });
    
  $(".consolidate").click(function () {
        var f = $(this).attr('name');
        var cto = $("#"+f).val();
        var cfr = $("#"+f+"_from").val();
        var dataString = "cfr=" + cfr +"&cto=" + cto;        
        $.ajax({
            url: "/tfc",
            type: "POST",
            dataType: "html",
            data: dataString,
            success: (function (data) {
            }
)
        });
        
    });
    
});