

function startTimer(){
    var data = $.ajax( {
        type: 'POST',
        url: `/quizbuilder/get_time_remaining/`,
        data: {
        },
        success: function(data) {  
        }
    });
}

function send(){
    
    var data = $.ajax( {
        type: 'GET',
        url: `/quizbuilder/hello/`,
        data: { 'url':'/memcreate'
        },
        success: function(data) {  
        }
    
    });
}
