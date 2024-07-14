let inactivityTime = function () {
    let time;
    window.onload = resetTimer;
    document.onmousemove = resetTimer;
    document.onkeypress = resetTimer;
    document.onscroll = resetTimer;
    document.onclick = resetTimer;

    function logout() {
        fetch('/auth/logout/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        }).then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = '/auth/login/';
            }
        });
    }

    function checkAuthStatus() {
        fetch('/check-auth/')
        .then(response => response.json())
        .then(data => {
            if (!data.authenticated) {
                window.location.href = '/auth/login/';
            }
        });
    }

    function resetTimer() {
        clearTimeout(time);
        time = setTimeout(logout, 5 * 60 * 1000); // 5 minutes
    }

    // Check auth status every minute
    setInterval(checkAuthStatus, 60 * 1000);
};

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

inactivityTime();