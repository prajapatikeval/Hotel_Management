function searchRoom() {
    var input, filter, rooms, room, title, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    rooms = document.querySelectorAll(".rooms_div");
    var noRoomsFound = document.getElementById("no-rooms-found");

    var found = false;

    $(input).on('input', function(e) {
        if('' == this.value) {
            for (i = 0; i < rooms.length; i++) {
                room = rooms[i];
                room.style.display = "";
            }
            noRoomsFound.style.display = "none";        
        }
    });

    for (i = 0; i < rooms.length; i++) {
        room = rooms[i];
        title = room.querySelector("#room_name");
        txtValue = title.textContent || title.innerText;

            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                room.style.display = "block";
                found = true;
            } 
            
            else {
                room.style.display = "none";
            }
        }
    
    if (found) {
        noRoomsFound.style.display = "none";
    } else {
        noRoomsFound.style.display = "block";
    }
}