"use strict";
(function ($) {
  $(document).ready(function () {
    const object = getChangedObject();
    if (object === null) {
      return;
    }
    $(".object-tools").prepend(getObjectNotificationComponent());
    initObjectNotificationDropdown($);
    addObjectNotificationHandlers($, object);
    addObjectNotificationWSHandlers($, object);
  });
})(django.jQuery);

// Returns the app label, model name and primary key of the object shown by
// an admin change view, or null on any other view.
//
// This script is added to the Media of every ModelAdmin listed in
// OPENWISP_NOTIFICATIONS_IGNORE_ENABLED_ADMIN, so it also runs on their add
// and changelist views, where it must do nothing. Those admins can belong to
// any app and may set their own change form template, hence the values are
// read from what Django's admin renders on every change view rather than
// from a template override:
// - the URL path ends with "/<pk>/change/", which no add or changelist URL
//   does (the query string is ignored, so popups match as well);
// - "admin/change_form.html" sets the "app-<app_label>" and
//   "model-<model_name>" classes on the body. They cannot tell the add view
//   from the change view, hence the URL check above. A change view whose
//   template does not extend it lacks them and gets no widget, as with the
//   former template override.
// Primary keys are used as they appear in the URL: keys the admin quotes
// (characters such as "/" or "_") are not supported.
function getChangedObject() {
  const match = /\/([^/]+)\/change\/?$/.exec(window.location.pathname);
  if (match === null) {
    return null;
  }
  const object = { id: match[1] };
  document.body.classList.forEach(function (name) {
    if (name.startsWith("app-")) {
      object.appLabel = name.slice("app-".length);
    } else if (name.startsWith("model-")) {
      object.modelName = name.slice("model-".length);
    }
  });
  if (!object.appLabel || !object.modelName) {
    return null;
  }
  return object;
}

function getObjectNotificationComponent() {
  return `
    <li class="ow-object-notification-container">
        <a href="#" id="ow-object-notify" class="ow-object-notify" title="You are receiving notifications for this object.">
            <span class="ow-icon ow-object-notify-bell"></span>
            <span id="ow-silence-label">Silence notifications</span>
        </a>
        <div class="ow-object-notification-option-container option-container ow-hide">
            <p id="ow-notification-help-text">Disable notifications for this object</p>
            <button data-days=0 class="ow-hide ow-notification-option" id="ow-enable-notification">Enable notifications for this object</button>
            <button data-days=1 class="ow-notification-option option disable-notification">1 Day</button>
            <button data-days=7 class="ow-notification-option option disable-notification">1 Week</button>
            <button data-days=30 class="ow-notification-option option disable-notification">1 Month</button>
            <button data-days=-1 class="ow-notification-option option disable-notification">Permanently</button>
            <div id="ow-object-notification-loader" class="ow-hide"><div class="loader"></div></div>
        </div>
    </li>
    `;
}

function initObjectNotificationDropdown($) {
  $(document).on("click", ".ow-object-notify", function (e) {
    e.preventDefault();
    $(".ow-object-notification-option-container").toggleClass("ow-hide");
  });
  $(document).click(function (e) {
    e.stopPropagation();
    // Check if the clicked area is dropDown / ow-notify-btn or not
    if (
      $(".ow-object-notification-option-container").has(e.target).length === 0 &&
      !$(e.target).is($(".ow-object-notify"))
    ) {
      $(".ow-object-notification-option-container").addClass("ow-hide");
    }
  });
  $(document).on("focusin", function (e) {
    // Hide dropdown while accessing dropdown through keyboard
    e.stopPropagation();
    if ($(".ow-object-notification-option-container").has(e.target).length === 0) {
      $(".ow-object-notification-option-container").addClass("ow-hide");
    }
  });
  $(".ow-object-notification-option-container").on("keyup", "*", function (e) {
    e.stopPropagation();
    // Hide dropdown on "Escape" key
    if (e.keyCode == 27) {
      $(".ow-object-notification-option-container").addClass("ow-hide");
      $("#ow-object-notify").focus();
    }
  });
}

function addObjectNotificationHandlers($, object) {
  // Click handler for disabling notifications
  $(document).on(
    "click",
    "button.ow-notification-option.disable-notification",
    function (e) {
      e.stopPropagation();
      let validTill,
        daysOffset = $(this).data("days");
      if (daysOffset === -1) {
        validTill = undefined;
      } else {
        validTill = new Date();
        validTill.setDate(validTill.getDate() + daysOffset);
        validTill = validTill.toISOString();
      }

      $.ajax({
        type: "PUT",
        url: getAbsoluteUrl(
          `/api/v1/notifications/notification/ignore/${object.appLabel}/${object.modelName}/${object.id}/`,
        ),
        headers: {
          "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val(),
        },
        xhrFields: {
          withCredentials: true,
        },
        beforeSend: function () {
          $(".ow-object-notification-option-container > button").addClass("ow-hide");
          $("#ow-object-notification-loader").removeClass("ow-hide");
        },
        data: {
          valid_till: validTill,
        },
        crossDomain: true,
        success: function () {
          updateObjectNotificationHelpText($, validTill);
          $("#ow-object-notification-loader").addClass("ow-hide");
        },
        error: function (error) {
          throw error;
        },
      });
    },
  );

  // Click handler for enabling notifications
  $(document).on("click", "#ow-enable-notification", function (e) {
    e.stopPropagation();
    $.ajax({
      type: "DELETE",
      url: getAbsoluteUrl(
        `/api/v1/notifications/notification/ignore/${object.appLabel}/${object.modelName}/${object.id}/`,
      ),
      headers: {
        "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val(),
      },
      xhrFields: {
        withCredentials: true,
      },
      beforeSend: function () {
        $(".ow-object-notification-option-container > button").addClass("ow-hide");
        $("#ow-object-notification-loader").removeClass("ow-hide");
      },
      crossDomain: true,
      success: function () {
        $("#ow-object-notify > span.ow-icon").removeClass(
          "ow-object-notify-slash-bell",
        );
        $("#ow-object-notify > span.ow-icon").addClass("ow-object-notify-bell");
        $("#ow-silence-label").html("Silence notifications");
        $("#ow-object-notify").prop(
          "title",
          "You are receiving notifications for this object.",
        );

        $("#ow-notification-help-text").html(`Disable notifications for this object`);
        $("#ow-object-notification-loader").addClass("ow-hide");
        $(".ow-notification-option.disable-notification").removeClass("ow-hide");
        $(".ow-object-notification-option-container > button:visible:first").focus();
      },
      error: function (error) {
        throw error;
      },
    });
  });
}

function addObjectNotificationWSHandlers($, object) {
  if (notificationSocket.readyState === 1) {
    openHandler();
  }
  notificationSocket.addEventListener("open", openHandler);

  notificationSocket.addEventListener("message", function (e) {
    let data = JSON.parse(e.data);
    if (data.type !== "object_notification") {
      return;
    }
    if (data.hasOwnProperty("valid_till")) {
      updateObjectNotificationHelpText($, data.valid_till);
    }
  });

  function openHandler() {
    let data = {
      type: "object_notification",
      object_id: object.id,
      app_label: object.appLabel,
      model_name: object.modelName,
    };
    notificationSocket.send(JSON.stringify(data));
  }
}

function updateObjectNotificationHelpText($, validTill) {
  let disabledText;
  if (validTill === null || validTill === undefined) {
    disabledText = `Disabled permanently`;
  } else {
    let dateTimeString = dateTimeStampToDateTimeLocaleString(new Date(validTill));
    disabledText = `Disabled till ${dateTimeString}`;
  }

  $("#ow-notification-help-text").html(disabledText);
  $("#ow-enable-notification").removeClass("ow-hide");
  $(".ow-notification-option.disable-notification").addClass("ow-hide");
  $(".ow-object-notification-option-container > button:visible:first").focus();

  $("#ow-object-notify > span.ow-icon").removeClass("ow-object-notify-bell");
  $("#ow-object-notify > span.ow-icon").addClass("ow-object-notify-slash-bell");
  $("#ow-silence-label").html("Unsilence notifications");
  $("#ow-object-notify").prop(
    "title",
    "You have disabled notifications for this object.",
  );
}
