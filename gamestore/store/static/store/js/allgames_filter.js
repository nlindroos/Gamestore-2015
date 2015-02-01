function search_by_name(name) {
   "use strict";
   var games = $("#gamelist h3").map(function() {
      // If not found
      if ($(this).html().toLowerCase().indexOf(name.toLowerCase()) === -1) {
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

function limit_by_price(limit, lower) {
   "use strict";
   limit = parseFloat(limit);
   var floatLimit = parseFloat(limit);

   $(".js-price").each(function() {
      var price = $(this).html().split(" ")[0];
      var floatPrice = parseFloat(price);
      var row = $(this).parents(".row").eq(0);
      // Lower limit changed
      if (lower) {
         if (price==="FREE!") {
            // isNaN added for when all input is deleted
            if (floatLimit===0 || isNaN(limit)) {
               row.removeClass("low");
               row.show();
               row.prev("h3").show();
            }
            else {
               row.addClass("low");
               row.hide(); // Hide the content of a game
               row.prev("h3").hide();  // Hide the header of a game
            }
         }
         // If the price of the game is lower than the lower limit
         else if (floatPrice < floatLimit) {
            row.addClass("low");
            row.hide();
            row.prev("h3").hide();
         }

         else if (!row.hasClass("high")) {
            row.removeClass("low");
            row.show();
            row.prev("h3").show();
         }
         else {
            row.removeClass("low");
         }
      }

      // Higher limit changed
      else if (!lower) {
         if (price!="FREE!") {
            if (floatPrice > floatLimit) {
               row.addClass("high");
               row.hide();
               row.prev("h3").hide();
            }
            else if (!row.hasClass("low")) {
               row.removeClass("high");
               row.show();
               row.prev("h3").show();
            }
            else {
               row.removeClass("high");
            }
         }
      }
   });
}

// Empties the input fields upon refresh
function resetForm() {
   "use strict";
   $("#js-search-form")[0].reset();
}

$(document).ready(function() {
   "use strict";
   resetForm();
   $("#name_filter").on('input', function() {
      search_by_name($(this).val());
   });
   $("#tag_filter").on('input', function() {
      search_by_tag($(this).val());
   });
   $("#price_filter_low").on('input', function() {
      limit_by_price($(this).val(), true);
   });
   $("#price_filter_high").on('input', function() {
      limit_by_price($(this).val(), false);
   });
});
