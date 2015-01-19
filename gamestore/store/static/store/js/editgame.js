$(document).ready( function() {
    "use strict";
    
    $("#addtag").click(function() {
        var count = $('[name="tags[]"]').length;
        var input_group = $('<div class="input-group"></div>');
        var input = $('<input type="text" name="tags[]" placeholder="awesome" class="form-control"></input>');
        input.attr("id", "tag" + count);
        input_group.append(input);
        var remove = $('<span class="input-group-addon" style="cursor: pointer;">Remove</span>');
        remove.attr("id", "delete_tag" + count);
        input_group.append(remove)
        input_group.insertBefore("#addtag");
    });
    $(".tag_remover").click(function() {
        $(this).parent().remove();
    });
});