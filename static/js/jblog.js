$(document).ready(function(){
        alert("ready?");
$(window).scroll(function(){
    var scrollTop = $(this).scrollTop();
    var scrollHeight = $(document).height();
    var windowHeight = $(this).height();
    if(scrollTop + windowHeight == scrollHeight){
        $("#fright").css('display','block');
    }
    else{
        $("#fright").css('display','none');
    }
});

$("#container").imagesLoaded().always(function(){
            var container = document.querySelector('#container');
            var msnry = new Masonry( container, {
                  columnWidth: ".sub",
                    itemSelector: '.article'
                    });
            $(".article").css('margin-left','4%');
        var documentHeight = $(document).height();
        var windowHeight = $(window).height();
        console.log(documentHeight,windowHeight);
        if (documentHeight==windowHeight){
            $("#fright").css('display','block');
        }
});
});

