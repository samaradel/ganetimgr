 $(document).ready(function () {

    var content = $('.content');
    var message_container = $('#jsonmessages');
    var messages_url = message_container.data('messages');

    $.add_message = function(text, css) {
        var css_class = 'alert-';
        if (css != undefined) {
            css_class += css;
        } else {
            css_class += 'warning';
        }
        var message_div = message_container.find('.message-template').clone();
        message_div.removeClass('message-template');
        message_div.find('span').text(text);
        message_div.addClass(css_class);
        message_container.append(message_div);
        content.removeClass('loading');
        message_container.show();
    }

	$(document).ajaxError(function(event, request, settings) {
        // in case of ajax Error
        if (request.status === 500) {
	 	     $.add_message('An error occured with your request');
        }
	});

    $(document).ajaxComplete(function(event, xhr, settings) {
        // in case an ajax request is completed
        if (xhr.readyState < 4) {
            xhr.abort();
        } else {
            content.removeClass('loading');
        }
    });

    $(document).ajaxSend(function() {
        // in case an ajax request is sent
        // This does NOT work with jquery datatables.
        content.addClass('loading');
    });

    $( document ).ajaxSuccess(function(event, xhr, settings) {
        if (settings.url != messages_url) {
            $.get( messages_url, function(data) {
                for (var i=0; i<data.length; i++) {
                    $.add_message(data[i].message, data[i].css);
                }
            });
        }
    });
});