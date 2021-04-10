const updateMissionsList = (missions) => {
    if (missions.length > 0) {
        let missionListHtml = [];

        missions.forEach(element => {
            let mission = element.mission[0];
            let uid = element.uid;

            // Create mission bloc
            let missionBlocClass = "row justify-content-between mb-2 w-75 list-group-item-action border-bottom";
            let divMissionBloc = $('<div></div>');
            divMissionBloc.addClass(missionBlocClass);

            // Create mission title bloc
            let missionTitleBlocClass = "col-md-6 d-flex flex-column font-weight-bold";
            let divMissionTitleBloc = $('<div></div>');
            divMissionTitleBloc.addClass(missionTitleBlocClass);
            divMissionTitleBloc.text(element.mission.fields.title);

            // Create mission category bloc
            let divMissionCategoryBloc = $('<small></small>');
            divMissionCategoryBloc.text("Catégorie : " + element.category.fields.label);

            // Create mission category bloc
            let divMissionRewardBloc = $('<small></small>');
            let totalRewardAmount = parseInt(element.category.fields.base_reward_amount) + parseInt(element.bonus_reward.fields.reward_amount);
            divMissionRewardBloc.text("Récompenses : " + element.category.fields.xp_amount + " xp et " + totalRewardAmount + " po");

            divMissionTitleBloc.append(divMissionCategoryBloc);
            divMissionTitleBloc.append(divMissionRewardBloc);

            // Create mission details button            
            let missionDetailsBtnClass = "col-md-2 btn btn-secondary mx-1 my-auto";
            let missionDetailsBtnBloc = $('<a></a>');
            let btnHref = "/mission/details/" + uid + "/";
            missionDetailsBtnBloc.attr('href', btnHref);
            missionDetailsBtnBloc.addClass(missionDetailsBtnClass);
            missionDetailsBtnBloc.text('détails');

            divMissionBloc.append(divMissionTitleBloc);
            divMissionBloc.append(missionDetailsBtnBloc);
            missionListHtml.push(divMissionBloc);
        });

        if ($('#missions-list').hasClass('justify-content-center')) {
            $('#missions-list').removeClass('justify-content-center');
        }
        $('#missions-list').empty();

        missionListHtml.forEach((missionBloc) => {            
            $('#missions-list').append(missionBloc);
        });
    }
    else {
        // Create empty mission bloc
        let emptyMissionBloc = $('<p></p>');
        emptyMissionBloc.text("Aucunes Missions")
        
        if (!$('#missions-list').hasClass('justify-content-center')) {
            $('#missions-list').addClass('justify-content-center');
        }
        $('#missions-list').empty();
        $('#missions-list').append(emptyMissionBloc);
    }
}

const getMissionsWithStatus = (statusName) => {
    $.ajax({
        type: "GET",
        url: $(location).attr('href') + '?status=' + statusName,
        success: (response) => {
            response.forEach(element => {
                element.mission = JSON.parse(element.mission)[0];
                element.category = JSON.parse(element.category)[0];
                element.bonus_reward = JSON.parse(element.bonus_reward)[0];
            });
            console.log(response);
            updateMissionsList(response);
        },
        error: (error) => {
            console.log(error.message);
        }
    });
}

$(document).ready(() => {
    let selectedFilter;

    if (!sessionStorage.getItem('missionFilter')) {
        selectedFilter = "open";
        sessionStorage.setItem('missionFilter', selectedFilter);
    }
    else {
        selectedFilter = sessionStorage.getItem('missionFilter');
    }

    $('.mission-status-filter').removeClass('active-filter');
    $('.mission-status-filter[status-name="' + selectedFilter + '"]').addClass('active-filter')

    $('.mission-status-filter').click((e) => {
        if ($(e.target).attr('status-name') !== selectedFilter) {
            selectedFilter = $(e.target).attr('status-name');
            sessionStorage.setItem('missionFilter', selectedFilter);;
            $('.mission-status-filter').removeClass('active-filter');
            $(e.target).addClass('active-filter');

            getMissionsWithStatus(selectedFilter);
        }
    })
})