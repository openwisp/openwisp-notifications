from openwisp_notifications.apps import OpenwispNotificationsConfig


class SampleNotificationsConfig(OpenwispNotificationsConfig):
    name = 'openwisp2.sample_notifications'
    label = 'sample_notifications'
    verbose_name = 'Notifications (custom)'
