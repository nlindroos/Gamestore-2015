function tag_input() {
    var text = $(this).val();
    if (text.indexOf(',', text.length - 1) !== -1) {
        $(this).val(text.slice(0, -1));
        add_tag();
    }
}

function add_tag() {
    var input_group = $('<div class="input-group"></div>');
    var input = $('<input type="text" name="tags[]" placeholder="awesome" class="form-control taginput"></input>');
    input_group.append(input);
    var remove = $('<span class="input-group-addon tag_remover">Remove</span>');
    remove.click(function() {
        $(this).parent().remove();
    });
    input.on('input', tag_input);
    input_group.append(remove);
    $('#tag_editor').append(input_group);
    input.focus();
}

function delete_game(e) {
    e.preventDefault();
    if (confirm("Are you sure you want to delete this game?")) {
        $("#deleteForm").submit();
    }
    return;
}

$(document).ready( function() {
    "use strict";
    
    $("#addtag").click(add_tag);
    $(".tag_remover").click(function() {
        $(this).parent().remove();
    });
    $('.taginput').on('input', tag_input);
    $("#deleteGame").click(function(e) {
        delete_game(e);
    });
});