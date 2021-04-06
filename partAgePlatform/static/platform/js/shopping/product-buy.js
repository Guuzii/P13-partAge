var timeOut;

const startTimeout = () => {
    timeOut = setTimeout(() => {
        $('#shopping-messages').hide();
    }, 3000);
};

const stopTimeout = () => {
    clearTimeout(timeOut);
};

const getUserTransactions = () => {
    $.ajax({
        type: "GET",
        url: $(location).attr('href') + '?history=1',
        success: (response) => {
            response.forEach(element => {
                element.product = JSON.parse(element.product)[0];
                element.transaction = JSON.parse(element.transaction)[0];
            });
            console.log('response history :', response);
            // updateMissionsList(response);
        },
        error: (error) => {
            console.log(error.message);
        }
    });
}

const getProductsList = () => {
    $.ajax({
        type: "GET",
        url: $(location).attr('href') + '?refresh=1',
        success: (response) => {
            response = JSON.parse(response);
            console.log('response refresh :', response);
            // updateMissionsList(response);
        },
        error: (error) => {
            console.log(error.message);
        }
    });
}

$(document).ready(() => {
    let selectedTab = "default";

    // Handle buying product
    $('.buy-product-form').submit((e) => {
        e.preventDefault();
        let csrfToken = $('[name="csrfmiddlewaretoken"]').val();

        $.ajax({
            type: "POST",
            url: $(e.target).attr('action'),
            data: {
                'csrfmiddlewaretoken': csrfToken
            },
            success: (response) => {
                if (timeOut) {                    
                    stopTimeout();
                }

                let messageLi = $('<li></li>');
                messageLi.text(response.message);

                if (response.valid) {
                    $('#user-balance').text(response.new_balance);
                    let productList = $('.product');
                    
                    for (let i = 0; i < productList.length; i++) {
                        const product = productList[i];
                        const productPrice = parseInt($(product).children().find('.product-price').text().split(' ')[0]);
                        if (response.new_balance < productPrice) {
                            $(product).children().find('.product-price').removeClass('text-success').addClass('text-danger');
                            $(product).children().find('.btn').removeClass('btn-success').addClass('btn-danger');
                        }
                    }
                    messageLi.addClass("alert alert-success success");
                }
                else {
                    messageLi.addClass("alert alert-danger error");
                }

                $('#shopping-messages').empty().append(messageLi).show();

                startTimeout();
            },
            error: (response) => {
                window.location.href = response;
            }
        });
    });

    // Shopping tab handle
    $('.shopping-tab').click((e) => {
        if ($(e.target).attr('tab-data') !== selectedTab) {
            selectedTab = $(e.target).attr('tab-data')
            $('.shopping-tab').removeClass('active-filter');
            $(e.target).addClass('active-filter');

            if (selectedTab == "default") {
                getProductsList();
            }
            else {
                getUserTransactions();
            }
        }
    })
});