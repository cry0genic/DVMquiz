

function startTimer(){
    var data = $.ajax( {
        type: 'POST',
        url: `/get_time_remaining/`,
        data: {
        },
        success: function(data) {  
        }
    });
}

function send(){
    
    var data = $.ajax( {
        type: 'GET',
        url: `/hello/`,
        data: { 'url':'/memcreate'
        },
        success: function(data) {  
        }
    
    });
}
