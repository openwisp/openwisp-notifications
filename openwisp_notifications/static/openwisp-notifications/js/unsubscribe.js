if (typeof gettext === 'undefined') {
    var gettext = function(word) { return word; };
}

function updateSubscription(subscribe) {
    const token = '{{ request.GET.token }}';

    fetch(window.location.href, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ subscribe: subscribe })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const toggleBtn = document.getElementById('toggle-btn');
            const statusMessage = document.getElementById('status-message');
            const confirmationMsg = document.getElementById('confirmation-msg');

            if (subscribe) {
                statusMessage.textContent = gettext('You are currently subscribed to notifications.');
                toggleBtn.textContent = gettext('Unsubscribe');
                confirmationMsg.textContent = data.message;
            } else {
                statusMessage.textContent = gettext('You are currently unsubscribed from notifications.');
                toggleBtn.textContent = gettext('Subscribe');
                confirmationMsg.textContent = data.message;
            }

            confirmationMsg.style.display = 'block';
        } else {
            alert(data.message);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggle-btn');
    toggleBtn.addEventListener('click', function() {
        const currentStatus = toggleBtn.textContent.trim().toLowerCase();
        const subscribe = currentStatus === gettext('subscribe').toLowerCase();
        updateSubscription(subscribe);
    });
});
