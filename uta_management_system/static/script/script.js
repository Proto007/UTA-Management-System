$(document).ready(function(){
    $(".alternate-day-selector").hide()
    hidden = true
    $(".alternate-toggle").on('click', function(){
        if (hidden == true){
            $(".alternate-day-selector").show()
            hidden = false
        }
        else{
            $(".alternate-day-selector").hide()
            hidden = true
        }
    })
    setTimeout(function() {
        $(".timeout").fadeOut('fast');
    }, 3000);
})

$(document).bind("contextmenu",function(e) {
    e.preventDefault();
});

$(document).keydown(function(e){
    if(e.which === 123){
        return false;
    }
});
