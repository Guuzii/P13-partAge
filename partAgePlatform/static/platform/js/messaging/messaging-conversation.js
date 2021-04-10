const diffMessagesArrayOnPk = (baseArray, updatedArray) => {
    return updatedArray.filter((current) => {
        return baseArray.filter(function(other){
            return other.pk == current.pk
        }).length == 0;
    })
}

const createAndAppendMessageHtml = (message, user, relatedUser, statusCreatedId) => {
    // Create message container
    let messageBoxClass = "message-box container position-relative mb-2";
    messageBoxClass += message.fields.sender_user === user.id ? " align-self-end mr-2 bg-secondary" : " align-self-start ml-2";
    let divMessageContainer = $('<div></div>');
    divMessageContainer.addClass(messageBoxClass);
    
    // Create message content
    let divMessageContentRow = $('<div></div>');
    divMessageContentRow.addClass("row mt-2 mb-2");
    let divMessageContentCol = $('<div></div>');
    divMessageContentCol.addClass(message.fields.sender_user === user.id ? "col-md-12 text-right text-white" : "col-md-12");
    divMessageContentCol.text(message.fields.content);

    // Create message infos
    let divMessageInfosRow = $('<div></div>');
    divMessageInfosRow.addClass("row mt-2");
    let divMessageInfosCol = $('<div></div>');
    divMessageInfosCol.addClass(message.fields.sender_user === relatedUser.id ? "col-md-12 text-right" : "col-md-12");
    let smallMessageInfos = $('<small></small>');
    smallMessageInfos.addClass("text-muted")
    let messageDate = new Date(message.fields.created_at);
    let formattedDate = messageDate.toLocaleDateString() + " " + messageDate.toLocaleTimeString();
    smallMessageInfos.text(
        message.fields.status === statusCreatedId ? "Envoyé le " + formattedDate + " par " 
            : "Modifié le " + formattedDate + " par "
    );
    let spanUserFullname = $('<span></span>');
    spanUserFullname.addClass("font-weight-bold");
    spanUserFullname.text(message.fields.sender_user === user.id ? user.fullname : relatedUser.fullname);
    
    // Put together all created elements
    divMessageContentRow.append(divMessageContentCol);
    smallMessageInfos.append(spanUserFullname);
    divMessageInfosCol.append(smallMessageInfos);
    divMessageInfosRow.append(divMessageInfosCol);
    divMessageContainer.append(divMessageContentRow, divMessageInfosRow);

    // Create and add check icon if sender is user
    if (message.fields.sender_user === user.id) {
        let spanMessageCheck = $('<span></span>');
        spanMessageCheck.addClass("message-received");
        if (message.fields.is_viewed) {
            spanMessageCheck.append('<i class="fas fa-check-circle text-primary">');
        }
        else {
            spanMessageCheck.append('<i class="far fa-check-circle text-white"></i>');
        }
        divMessageContainer.append(spanMessageCheck);
    }

    divMessageContainer.insertBefore("#last-message-ref");
    
    // scrollToLastMessage();
}

const scrollToLastMessage = (animate=true) => {
    // console.log('SCROLL');
    let lastMessageRef = $('#last-message-ref');
    if (lastMessageRef.length){
        if (animate) {
            $('#messages-list').animate({
                scrollTop: (lastMessageRef.offset().top)
            }, 1000);
        }
        else {
            $('#messages-list').scrollTop(lastMessageRef.offset().top);
        }
    }
    return false
}

$(document).ready(() => {
    let actualMessagesList;
    let user;
    let relatedUser;
    let statusCreatedId;
    let lastKeyPress;

    scrollToLastMessage(false);

    // Initiate messages list
    $.ajax({
        type: "GET",
        url: $(location).attr('href') + '?refresh=1',
        success: (response) => {
            actualMessagesList = response;
        }
    });

    // Get conversation infos
    $.ajax({
        type: "GET",
        url: $(location).attr('href') + '?infos=1',
        success: (response) => {
            user = response.user;
            relatedUser = response.related_user;
            statusCreatedId = response.status_created_id;
        }
    });

    // Check for messages updates
    setInterval(() => {
        $.ajax({
            type: "GET",
            url: $(location).attr('href') + '?refresh=1',
            success: (response) => {
                let diffMessages = diffMessagesArrayOnPk(actualMessagesList, response);

                if (diffMessages.length > 0) {
                    actualMessagesList = response;

                    diffMessages.forEach(message => {
                        createAndAppendMessageHtml(message, user, relatedUser, statusCreatedId)
                    });
                }
            }
        });
    }, 5000); // in milliseconds

    // Handle sending message
    $('#send-message-form').submit((e) => {
        e.preventDefault();
        $('.form-errors').empty();

        let messageContent = $('#id_message_content').val();
        let csrfToken = $('[name="csrfmiddlewaretoken"]').val();

        $.ajax({
            type: "POST",
            url: $(location).attr('href'),
            data: {
                'csrfmiddlewaretoken': csrfToken,
                'message_content': messageContent
            },
            success: (response) => {
                $('#id_message_content').val('');
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

})

