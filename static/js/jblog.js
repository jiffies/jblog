$(document).ready(function(){
//$(window).scroll(function(){
    //var scrollTop = $(this).scrollTop();
    //var scrollHeight = $(document).height();
    //var windowHeight = $(this).height();
    //if(scrollTop + windowHeight == scrollHeight){
        //$("#fright").css('display','block');
    //}
    //else{
        //$("#fright").css('display','none');
    //}
//});
    $('.button-submit').click(function(){
        $('#container form').submit();
    });

    $(".a_post").click(function(e){
        e.preventDefault();
        $.ajax({
            url:$(this).attr('data'),
            type:'POST',
            success:function(data,textstatus,jqXHR){
                var url = JSON.parse(data).data
                console.log(url);
                window.location.href = url;
                //window.location.reload();
            },
            dataType:'text'
        });
    });
    var fleftHeight = $('#fleft').height();
    $('#social-icons').css('top',-(fleftHeight+8));
    $('#fright').css('height',fleftHeight);
    $('.footer-text').css('line-height',fleftHeight.toString()+'px');
$(window).resize(function(){
    var fleftHeight = $('#fleft').height();
    $('#social-icons').css('top',-(fleftHeight+8));
    $('#fright').css('height',fleftHeight);
    $('.footer-text').css('line-height',fleftHeight.toString()+'px');
});
$("#container").imagesLoaded().always(function(){
            var container = document.querySelector('#container-inner');
            var msnry = new Masonry( container, {
                  columnWidth: ".sub",
                    itemSelector: '.article'
                    });
            //$(".article").css('margin-left','4%');
        var documentHeight = $(document).height();
        var windowHeight = $(window).height();
        console.log(documentHeight,windowHeight);
        //if (documentHeight==windowHeight){
            //$("#fright").css('display','block');
        //}
        var uyan = document.querySelector('#uyan_frame');
        if(!uyan){
            if($(window).height()==$('#container').height()){
                $('#fright').css('position','absolute');
                $('#fright').css('width','74%');
                $('#fright').css('bottom','0px');
            };
        };
});
});

