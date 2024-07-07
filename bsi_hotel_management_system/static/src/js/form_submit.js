odoo.define('bsi_hotel_management_system.form_submit', function(require){
    'use strict'

    var ajax = require('web.ajax');

    $('#check_booking_availablity').on('submit', function(e){
        e.preventDefault();

        var check_in = $('#date-in').val().trim();
        var form_room_id = $('#form_room_id').val().trim();
        var check_out = $('#date-out').val().trim();
        var room = $('#room').val().trim();

        var message = document.getElementById('success')
        var danger = document.getElementById('danger')
        var notsuccess = document.getElementById('notsuccess')

        if (check_out < check_in){
            danger.style.visibility = 'visible'

            setTimeout(() => {
                danger.style.visibility = 'hidden';
            },8000);
        }
        else{
            ajax.jsonRpc('/check_booking/','call',{'room_id':form_room_id,'date-in':check_in,'date-out':check_out, 'room':room}).then(function(result){
                if (result){
                    message.style.visibility = 'visible';
                    setTimeout(() => {
                        message.style.visibility = 'hidden';
                    },8000);
                }
                else{
                    notsuccess.style.visibility = 'visible';
                    setTimeout(() => {
                        notsuccess.style.visibility = 'hidden';
                    },8000);
                }
            })
        }
        // var submitmessage = form_room_id  
        // $.ajax({
        //     type : 'POST',
        //     url : submitmessage,
        //     data : $(this).serialize(),
        //     headers: {
        //         'X-Requested-With': 'XMLHttpRequest',
        //         // 'X-CSRFToken': csrfToken
        //     },
        //     success : function(data){
        //         success.style.display = 'block';
                
        //         setTimeout(() => {
        //             success.style.display = 'none';
        //         },3000);

        //     },
        // })



    });
    // $('#create_booking_form').on('submit', function(e){
    //     e.preventDefault();

        
    //     var form_room_booking_id = $('#form_room_booking_id').val().trim();
    //     var name = $('#name').val().trim();
    //     var phone = $('#phone').val().trim();
    //     var street = $('#street').val().trim();
    //     var email = $('#email').val().trim();
    //     var country = $('#country').val().trim();
    //     var state = $('#state').val().trim();
    //     var check_in = $('#date-in').val().trim();
    //     var check_out = $('#date-out').val().trim();
    //     var room = $('#room').val().trim();

    //     var booking_message = document.getElementById('booking_success')
    //     var booking_danger = document.getElementById('booking_danger')
    //     var booking_notsuccess = document.getElementById('booking_notsuccess')

    //     if (check_out < check_in){
    //         booking_danger.style.display = 'block'

    //         setTimeout(() => {
    //             booking_danger.style.display = 'none';
    //         },8000);
    //     }
    //     else{
    //         ajax.jsonRpc('/create/booking','call',{
    //             'room_id':form_room_booking_id,
    //             'name': name,
    //             'phone': phone,
    //             'street': street,
    //             'email': email,
    //             'country': country,
    //             'state': state,
    //             'date-in':check_in,
    //             'date-out':check_out, 
    //             'room':room
    //         }).then(function(result){
    //             console.log(result)
    //             if (result){
    //                 booking_message.style.display = 'block';
    //                 setTimeout(() => {
    //                     booking_message.style.display = 'none';
    //                 },8000);
    //             }
    //             else{
    //                 booking_notsuccess.style.display = 'block';
    //                 setTimeout(() => {
    //                     booking_notsuccess.style.display = 'none';
    //                 },8000);
    //             }
    //         })
    //     }
    // })
})
