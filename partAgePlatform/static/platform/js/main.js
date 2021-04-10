$(document).ready(() => {
    $('#btn-profile-dc').click((e) => {
        sessionStorage.clear();
    })

    setTimeout(() => {
        $('.messages').hide();
    }, 5000);
});