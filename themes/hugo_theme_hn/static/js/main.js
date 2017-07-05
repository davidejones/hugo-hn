function timeSince(date) {
    var seconds = Math.floor((new Date() - date) / 1000);
    var interval = Math.floor(seconds / 31536000);
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

var elements = document.getElementsByClassName('timeago');
for (var i = 0; i < elements.length; ++i) {
    var el = elements[i];
    var dtString = el.getAttribute('data-date');
    var b = dtString.split(/\D/);
    var dt = new Date(b[0],b[1]-1,b[2],b[3],b[4],b[5]);
    el.innerHTML = timeSince(dt);
}
