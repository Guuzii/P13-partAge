$(document).ready(() => {
    // Get stats numbers on page init
    $.ajax({
        type: "GET",
        url: "/user/" + '?statsnum=1',
        success: (response) => {
            $('#registered_user_count').text(response.user_count > 0 ? response.user_count : 0)
            $('#created_mission_count').text(response.mission_count > 0 ? response.mission_count : 0)
            $('#ended_mission_count').text(response.mission_end_count > 0 ? response.mission_end_count : 0)
        },
        error: (error) => {
            console.log(error.message);
        }
    });
});