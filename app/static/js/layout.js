span = document.querySelector('.navbar-toggler-icon');
let bind = 0;

span.addEventListener('click', function (e) {
    if (bind == 0) {
        span.className = 'navbar-toggler-icon nav-on';
        bind = 1;
    } else {
        span.className = 'navbar-toggler-icon nav-off';
        bind = 0;
    }
});