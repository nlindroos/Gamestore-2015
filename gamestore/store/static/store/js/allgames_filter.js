function search_by_name(name) {
   "use strict";
   var games = $("#gamelist h3").map(function() {
      // If not found
      if ($(this).html().toLowerCase().indexOf(name) === -1) {
         $(this).next().hide();
         $(this).hide();
      }
      else {
         $(this).next().show();
         $(this).show();
      }
   });
}

function search_by_tag(tagstring) {
   "use strict";
   var games = $("#gamelist h3").map(function() {
      var tags = tagstring.split();
      var hide = false;
      
      //ok, so we need to filter out the ones where
      //    one or more of the tags is not matched by any of the <li> contents
      
      //for each tag searched for:
      for (var i = 0; i < tags.length; i++) {
         var this_tags = $(this).next().children().eq(2).find('li');
         var found = false;
         //for each tag of the game:
         for (var j = 0; j < this_tags.length; j++) {
            //if tags match:
            if (this_tags.eq(j).html().indexOf(tags[i]) !== -1) {
               found = true;
               break;
            }
         }
         //if any of the searched tags was not found:
         if (!found) {
            hide = true;
            break;
         }
      }
      if (hide) {
         $(this).next().hide();
         $(this).hide();
      }
      else {
         $(this).next().show();
         $(this).show();
      } 
   });
}

$(document).ready(function() {
   "use strict";
   $("#name_filter").on('input', function() {
      search_by_name($(this).val());
   });
   $("#tag_filter").on('input', function() {
      search_by_tag($(this).val());
   });
});