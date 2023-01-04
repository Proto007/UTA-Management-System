function openForm() {
    document.getElementById("myForm").style.display = "block";
}

function closeForm() {
    document.getElementById("myForm").style.display = "none";

    $('#container').css({
        '-webkit-filter':'none',
        '-moz-filter':'none',
        '-o-filter':'none',
        '-ms-filter':'none',
        'filter':'none',
    })
    const bg = document.getElementById("background");
    bg.style = "background-color: rebeccapurple";
    bg.style.height = '50%';
}

window.onload = function() {
    openForm();
};

function validate($code){
    return $code == 1;
}

$(document).bind("contextmenu",function(e) {
    e.preventDefault();
});

$(document).keydown(function(e){
    if(e.which === 123){
        return false;
    }
});