$(document).ready(function(){
    $(".alternate-day-selector").hide()
    $(".alternate-toggle").on('click', function(){
        if ($(this).prop("checked") === true){
            $(".alternate-day-selector").show()
        }
        else{
            $(".alternate-day-selector").hide()
            $(".alternate-day-selector").prop('selectedIndex', 0);
        }
    })
    setTimeout(function() {
        $(".timeout").alert('close');
    }, 2500);
})

$(document).bind("contextmenu",function(e) {
    e.preventDefault();
});

$(document).keydown(function(e){
    if(e.which === 123){
        return false;
    }
});
