var userBalance;

const updateMissionTotalCost = (selectedCategoryPk, selectedBonusAmount) => {
    $.ajax({
        type: "GET",
        url: $(location).attr('href') + '?category_pk=' + selectedCategoryPk,
        success: (response) => {
            let totalMissionCost = response + parseInt(selectedBonusAmount);
            if (userBalance < totalMissionCost) {
                $('#mission-total-cost').removeClass("text-success").addClass("text-danger");
            }
            else {
                $('#mission-total-cost').removeClass("text-danger").addClass("text-success");
            }
            $('#mission-total-cost').text(totalMissionCost + " po");
        },
        error: (error) => {
            console.log(error.message);
        }
    });
    
}

$(document).ready(() => {
    // Get user balance on page init
    $.ajax({
        type: "GET",
        url: $(location).attr('href') + '?balance=1',
        success: (response) => {
            userBalance = response;    
            updateMissionTotalCost($('#id_mission_category').val(), $('#id_mission_bonus_amount').val());
        },
        error: (error) => {
            console.log(error.message);
        }
    });

    $('#id_mission_category').change((e) => {
        updateMissionTotalCost($('#id_mission_category').val(), $('#id_mission_bonus_amount').val());
    });
    $('#id_mission_bonus_amount').change((e) => {
        updateMissionTotalCost($('#id_mission_category').val(), $('#id_mission_bonus_amount').val());
    });
});