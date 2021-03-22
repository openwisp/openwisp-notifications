import swapper
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Permission
from django.db import migrations


def get_swapped_model(apps, app_name, model_name):
    model_path = swapper.get_model_name(app_name, model_name)
    app, model = swapper.split(model_path)
    return apps.get_model(app, model)


def create_default_groups(apps, schema_editor):
    group = get_swapped_model(apps, 'openwisp_users', 'Group')

    # To populate all the permissions
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None

    operator = group.objects.filter(name='Operator')
    if operator.count() == 0:
        operator = group.objects.create(name='Operator')
    else:
        operator = operator.first()

    admin = group.objects.filter(name='Administrator')
    if admin.count() == 0:
        admin = group.objects.create(name='Administrator')
    else:
        admin = admin.first()
    permissions = [
        Permission.objects.get(
            content_type__app_label='openwisp_notifications',
            codename='add_notification',
        ).pk,
        Permission.objects.get(
            content_type__app_label='openwisp_notifications',
            codename='change_notification',
        ).pk,
        Permission.objects.get(
            content_type__app_label='openwisp_notifications',
            codename='delete_notification',
        ).pk,
    ]
    permissions += operator.permissions.all()
    operator.permissions.set(permissions)

    permissions += admin.permissions.all()
    admin.permissions.set(permissions)


class Migration(migrations.Migration):
    dependencies = [
        ('openwisp_notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_default_groups, reverse_code=migrations.RunPython.noop
        ),
    ]
