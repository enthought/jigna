$(document).ready(
    function(){
        $('.hoverme').hover(
            function(){
                $(this).css('color', 'red');
            },
            function(){
                $(this).css('color', 'black');
            }
        )
    }
)
