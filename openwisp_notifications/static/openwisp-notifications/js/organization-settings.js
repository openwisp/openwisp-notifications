"use strict";
(function ($) {
  $(document).ready(function () {
    const webNotificationEnabled = $("#id_notification_settings-0-web");
    const emailNotificationEnabled = $("#id_notification_settings-0-email");

    $(webNotificationEnabled).on("change", function () {
      if (webNotificationEnabled.val() === "False") {
        // Disable email notifications if web notifications are disabled
        emailNotificationEnabled.prop("disabled", true);
        emailNotificationEnabled.val("False");
      } else {
        // Enable email notifications if web notifications are enabled
        emailNotificationEnabled.prop("disabled", false);
      }
    });
  });
})(django.jQuery);
