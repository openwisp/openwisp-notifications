_test_batch_email_notification_email_body = """
[example.com] 4 new notifications since {datetime_str}


- Default notification with default verb and level info by Tester Tester (test org)
  Description: Test Notification
  Date & Time: {datetime_str}
  URL: https://example.com/api/v1/notifications/notification/{notification_id}/redirect/

- Test Notification
  Description: Test Notification
  Date & Time: {datetime_str}

- Test Notification
  Description: Test Notification
  Date & Time: {datetime_str}
  URL: https://localhost:8000/admin

- Test Notification
  Description: Test Notification
  Date & Time: {datetime_str}
  URL: https://localhost:8000/admin
"""

_test_batch_email_notification_email_html = """
<div class="subject">[example.com] 4 new notifications since {datetime_str}</div>
<div>
    <div class="alert info">
        <h2><span class="badge info">INFO</span><span class="title"><a
                    href="https://example.com/api/v1/notifications/notification/{notification_id}/redirect/"
                    target="_blank">
                    <p>Default notification with default verb and level info by Tester Tester (test org)</p>
                </a></span></h2>
        <p>{datetime_str}</p>
        <p>
            <p>Test Notification</p>
        </p>
    </div>
    <div class="alert info">
        <h2><span class="badge info">INFO</span><span class="title">
                <p>Test Notification</p>
            </span></h2>
        <p>{datetime_str}</p>
        <p>
            <p>Test Notification</p>
        </p>
    </div>
    <div class="alert info">
        <h2><span class="badge info">INFO</span><span class="title"><a href="https://localhost:8000/admin"
                    target="_blank">
                    <p>Test Notification</p>
                </a></span></h2>
        <p>{datetime_str}</p>
        <p>
            <p>Test Notification</p>
        </p>
    </div>
    <div class="alert info">
        <h2><span class="badge info">INFO</span><span class="title"><a href="https://localhost:8000/admin"
                    target="_blank">
                    <p>Test Notification</p>
                </a></span></h2>
        <p>{datetime_str}</p>
        <p>
            <p>Test Notification</p>
        </p>
    </div>
</div>
"""
