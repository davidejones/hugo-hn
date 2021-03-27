function timeSince(date) {
    let seconds = Math.floor((new Date() - date) / 1000);
    let interval = Math.floor(seconds / 31536000);
    if (interval > 1) {
        return interval + " years ago";
    }
    interval = Math.floor(seconds / 2592000);
    if (interval > 1) {
        return interval + " months ago";
    }
    interval = Math.floor(seconds / 86400);
    if (interval > 1) {
        return interval + " days ago";
    }
    interval = Math.floor(seconds / 3600);
    if (interval > 1) {
        return interval + " hours ago";
    }
    interval = Math.floor(seconds / 60);
    if (interval > 1) {
        return interval + " minutes ago";
    }
    return Math.floor(seconds) + " seconds ago";
}

let elements = document.getElementsByClassName('timeago');
for (let i = 0; i < elements.length; ++i) {
    let el = elements[i];
    let dtString = el.getAttribute('data-date');
    let b = dtString.split(/\D/);
    let dt = new Date(b[0],b[1]-1,b[2],b[3],b[4],b[5]);
    el.innerHTML = timeSince(dt);
}

function myChangeHandler(el) {
    window.location.assign(el.options[el.selectedIndex].value);
}
