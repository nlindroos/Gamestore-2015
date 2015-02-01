$(document).ready( function() {
    "use strict";
    
    $("#addtag").click(function() {
        var input_group = $('<div class="input-group"></div>');
        var input = $('<input type="text" name="tags[]" placeholder="awesome" class="form-control"></input>');
        input_group.append(input);
        var remove = $('<span class="input-group-addon tag_remover">Remove</span>');
        remove.click(function() {
            $(this).parent().remove();
        });
        input_group.append(remove)
        $('#tag_editor').append(input_group);
    });
    $(".tag_remover").click(function() {
        $(this).parent().remove();
    });
});