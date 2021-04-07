var timeOut;
var userBalance;
var csrfToken;

const startTimeout = () => {
    timeOut = setTimeout(() => {
        $('#shopping-messages').hide();
    }, 3000);
};

const stopTimeout = () => {
    clearTimeout(timeOut);
};

const submitForm = (e) => {
    e.preventDefault();

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
                userBalance = response.new_balance;
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
}

const updateShopList = (shopList) => {    
    if (shopList.length > 0) {
        let shopListHtml = [];

        shopList.forEach(element => {
            // Create product bloc
            let productBlocClass = "product row w-100 list-group-item-action border-bottom py-2";
            let divProductBloc = $('<div></div>');
            divProductBloc.addClass(productBlocClass);

            // Create product img container
            let productImgBlocClass = "col-md-4 d-flex justify-content-center align-items-center";
            let divProductImgBloc = $('<div></div>');
            divProductImgBloc.addClass(productImgBlocClass);

            //Create product img
            let productImgTag = $('<img></img>');
            let imgSrc = element.transaction ? element.product.fields.path_to_sprite : element.fields.path_to_sprite;
            productImgTag.addClass("w-50");
            productImgTag.attr('src', imgSrc ? imgSrc : "/static/platform/assets/img/default.png");
            productImgTag.attr('alt', "Image du produit");

            divProductImgBloc.append(productImgTag)
            divProductBloc.append(divProductImgBloc)

            // Create product infos bloc           
            let productInfosBlocClass = "product-infos-bloc col-md-8 d-flex justify-content-between align-items-center";
            let productInfosBloc = $('<div></div>');
            productInfosBloc.addClass(productInfosBlocClass);

            // Create product label bloc
            let productLabelBloc = $('<div></div>');
            productLabelBloc.addClass("product-infos font-weight-bold");
            productLabelBloc.text(element.transaction ? element.product.fields.label : element.fields.label)

            // Create product description bloc
            let productDescriptionBloc = $('<small></small>');
            productDescriptionBloc.text(element.transaction ? element.product.fields.description : element.fields.description)

            productLabelBloc.append($('<br>'));
            productLabelBloc.append(productDescriptionBloc);
            productInfosBloc.append(productLabelBloc);

            // Create product buy/transaction bloc
            let productBuyBloc = $('<div></div>');
            productBuyBloc.addClass("product-buy d-flex align-items-center");

            if (element.transaction) {
                productBuyBloc.addClass("flex-column");
                productBuyBloc.attr('style', "max-width: 250px;")
                
                // Create transaction num bloc
                let transactionNumBloc = $('<div></div>');
                transactionNumBloc.text("Transaction n° ")

                // Create transaction num span
                let transactionNumSpan = $('<span></span>');
                transactionNumSpan.addClass("font-weight-bold");
                transactionNumSpan.text(element.transaction.pk);

                transactionNumBloc.append(transactionNumSpan);

                // Create transaction date bloc
                let transactionDateBloc = $('<div></div>');
                transactionDateBloc.addClass("text-center");
                transactionDateBloc.text("Effectuée le ")

                // Create transaction date span
                let createDate = new Date(Date.parse(element.transaction.fields.created_at));
                let transactionDateSpan = $('<span></span>');
                transactionDateSpan.addClass("font-weight-bold");                
                transactionDateSpan.text(createDate.toLocaleString('fr'));

                transactionDateBloc.append($('<br>'))
                transactionDateBloc.append(transactionDateSpan)
                
                // Assemble elements
                productBuyBloc.append(transactionNumBloc);
                productBuyBloc.append(transactionDateBloc);

                productInfosBloc.append(productBuyBloc);
            }
            else {
                // Create product price bloc
                let productPriceBloc = $('<div></div>');
                productPriceBloc.addClass("font-weight-bold mr-3");
                productPriceBloc.text("Prix : ")

                //Create product price span
                let productPriceSpanClass = "product-price";
                productPriceSpanClass += parseInt(userBalance) < parseInt(element.fields.price) ? " text-danger" : " text-success";
                let productPriceSpan = $('<span></span>');
                productPriceSpan.addClass(productPriceSpanClass);
                productPriceSpan.text(element.fields.price + "po");

                // Create product buy form
                let productBuyForm = $('<form></form>');
                productBuyForm.addClass("buy-product-form");
                productBuyForm.attr('action', "/shop/buy/" + element.pk + "/");
                productBuyForm.attr('method', "post");
                productBuyForm.submit((e) => {
                    submitForm(e)
                });

                // Create csrf input
                let productBuyCsrfInput = $('<input />');
                productBuyCsrfInput.attr('type', "hidden");
                productBuyCsrfInput.attr('name', "csrfmiddlewaretoken");
                productBuyCsrfInput.attr('value', csrfToken);

                // Create submit input
                let productBuySubmitInputClass = "btn btn-success btn-outline mx-1";
                productBuySubmitInputClass += parseInt(userBalance) < parseInt(element.fields.price) ? " btn-danger" : " btn-success";
                let productBuySubmitInput = $('<input />');
                productBuySubmitInput.addClass(productBuySubmitInputClass);
                productBuySubmitInput.attr('type', "submit");
                productBuySubmitInput.attr('value', "Acheter");
                
                // Assemble elements
                productPriceBloc.append(productPriceSpan);
                productBuyForm.append(productBuyCsrfInput);
                productBuyForm.append(productBuySubmitInput);

                productBuyBloc.append(productPriceBloc);
                productBuyBloc.append(productBuyForm);

                productInfosBloc.append(productBuyBloc);
            }
            
            divProductBloc.append(productInfosBloc);
            shopListHtml.push(divProductBloc);
        });

        if ($('#products-list').hasClass('justify-content-center')) {
            $('#products-list').removeClass('justify-content-center');
        }
        $('#products-list').empty();

        shopListHtml.forEach((productBloc) => {      
            $('#products-list').append(productBloc);
        });
    }
}

const getUserTransactions = () => {
    $.ajax({
        type: "GET",
        url: $(location).attr('href') + '?history=1',
        success: (response) => {
            response.forEach(element => {
                element.product = JSON.parse(element.product)[0];
                element.transaction = JSON.parse(element.transaction)[0];
            });
            updateShopList(response);
            console.log(response);
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
            updateShopList(response);
        },
        error: (error) => {
            console.log(error.message);
        }
    });
}

$(document).ready(() => {
    let selectedTab = "default";

    // Get csrf token on page init
    $.ajax({
        type: "GET",
        url: $(location).attr('href') + '?csrf=1',
        success: (response) => {
            csrfToken = response;
        },
        error: (error) => {
            console.log(error.message);
        }
    });

    // Get user balance on page init
    $.ajax({
        type: "GET",
        url: $(location).attr('href') + '?balance=1',
        success: (response) => {
            userBalance = response;
        },
        error: (error) => {
            console.log(error.message);
        }
    });

    // Handle buying product
    $('.buy-product-form').submit((e) => {
        submitForm(e)
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