// (function($) {
//   'use strict';
//   $('#exampleModal-4').on('show.bs.modal', function(event) {
//     var button = $(event.relatedTarget) // Button that triggered the modal
//     window._id = button.val()
//     var recipient = button.data('whatever') // Extract info from data-* attributes
//     // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
//     // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
//     var modal = $(this)
//     modal.find('.modal-title').text('New message to ' + recipient)
//     modal.find('.modal-body input').val(recipient)
//   })
// })(jQuery);

var modal = $('.modal');
var btn = null;
$(document).on('click', '.open-modal', function(e) {
    btn = $(this);
    btn.addClass('opened-modal');
    modal.show();
    window._id = btn.val()
    modal.find('.modal-header').append('Clicked: ' + $(this).html());
    $(document).on('click', '#btnSave', function(e) {

        // code here to update DB

        // Now need to set the data-text attribute value to "text" variable.
        btn.attr('data-text', text);
        btn.removeClass('opened-modal');
        modal.hide();
    });
    $(document).on('click', '#btnClose', function(e) {
        var btn = null;
        modal.hide();
    });
});