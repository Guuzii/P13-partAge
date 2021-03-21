$(document).ready(() => {
    let missionId;
    let lastKeyPress;
    
    $.ajax({
        type: "GET",
        url: $(location).attr('href') + '?infos=1',
        success: (response) => {
            missionId = response;
        }
    });

    // Handle sending message
    $('#send-message-form').submit((e) => {
        e.preventDefault();
        $('.form-errors').empty();

        let messageContent = $('#id_message_content').val();
        let csrfToken = $('[name="csrfmiddlewaretoken"]').val();

        $.ajax({
            type: "POST",
            url: $('#send-message-form').attr('action'),
            data: {
                'csrfmiddlewaretoken': csrfToken,
                'message_content': messageContent
            },
            success: (response) => {
                $('#id_message_content').val('');
                window.location.href = response;
            },
            error: (response) => {
                var r = jQuery.parseJSON(response.responseText);
                r.message_content.forEach(error => {                        
                    $('.form-errors').append('<span class="error">'+ error.message + '</span>')
                });
                $('#id_message_content').val('');
            }
        });
    });
    
    // Allow form submit with enter key when in textarea
    $('#id_message_content').keydown((e) => {
        if (lastKeyPress === 'Shift' && e.key === 'Enter') {
            e.preventDefault();
            $('#send-message-form').submit();
        }
        lastKeyPress = e.key;
    })

});