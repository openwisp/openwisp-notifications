"use strict";
if (typeof gettext === "undefined") {
  var gettext = function (word) {
    return word;
  };
}

function updateSubscription(subscribe) {
  fetch(window.location.href, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ subscribe: subscribe }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        const toggleBtn = document.getElementById("toggle-btn");
        const statusMessage = document.getElementById("status-message");
        const confirmationMsg = document.getElementById("confirmation-msg");

        if (subscribe) {
          statusMessage.textContent = gettext(
            "You are currently subscribed to notifications."
          );
          toggleBtn.textContent = gettext("Unsubscribe");
          toggleBtn.setAttribute("data-hasSubscribe", "true");
        } else {
          statusMessage.textContent = gettext(
            "You are currently unsubscribed from notifications."
          );
          toggleBtn.textContent = gettext("Subscribe");
          toggleBtn.setAttribute("data-hasSubscribe", "false");
        }

        confirmationMsg.textContent = data.message;
        confirmationMsg.style.display = "block";
      } else {
        window.alert(data.message);
      }
    })
    .catch((error) => {
      window.console.error("Error:", error);
    });
}

document.addEventListener("DOMContentLoaded", function () {
  const toggleBtn = document.getElementById("toggle-btn");
  toggleBtn.addEventListener("click", function () {
    const isSubscribed = toggleBtn.getAttribute("data-hasSubscribe") === "true";
    const subscribe = !isSubscribed;
    updateSubscription(subscribe);
  });
});
