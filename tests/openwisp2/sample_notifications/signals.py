from django.dispatch import Signal

test_app_name_changed = Signal(providing_args=['instance'])
