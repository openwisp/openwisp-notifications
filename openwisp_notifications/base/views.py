import base64
import json

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from openwisp_notifications.swapper import load_model

from ..tokens import email_token_generator

User = get_user_model()
NotificationSetting = load_model('NotificationSetting')


@method_decorator(csrf_exempt, name='dispatch')
class UnsubscribeView(TemplateView):
    template_name = 'openwisp_notifications/unsubscribe.html'

    def get(self, request, *args, **kwargs):
        encoded_token = request.GET.get('token')
        if not encoded_token:
            return render(request, self.template_name, {'valid': False})

        user, valid = self._validate_token(encoded_token)
        if not valid:
            return render(request, self.template_name, {'valid': False})

        is_subscribed = self.get_user_preference(user)

        return render(
            request,
            self.template_name,
            {
                'valid': True,
                'user': user,
                'is_subscribed': is_subscribed,
            },
        )

    def post(self, request, *args, **kwargs):
        encoded_token = request.GET.get('token')
        if not encoded_token:
            return JsonResponse(
                {'success': False, 'message': 'No token provided'}, status=400
            )

        user, valid = self._validate_token(encoded_token)
        if not valid:
            return JsonResponse(
                {'success': False, 'message': 'Invalid or expired token'}, status=400
            )

        subscribe = False
        if request.body:
            try:
                data = json.loads(request.body)
                subscribe = data.get('subscribe', False)
            except json.JSONDecodeError:
                return JsonResponse(
                    {'success': False, 'message': 'Invalid JSON data'}, status=400
                )

        self.update_user_preferences(user, subscribe)

        status_message = 'subscribed' if subscribe else 'unsubscribed'
        return JsonResponse(
            {'success': True, 'message': f'Successfully {status_message}'}
        )

    def _validate_token(self, encoded_token):
        try:
            decoded_data = base64.urlsafe_b64decode(encoded_token).decode()
            data = json.loads(decoded_data)
            user_id = data.get('user_id')
            token = data.get('token')

            user = User.objects.get(id=user_id)
            if email_token_generator.check_token(user, token):
                return user, True
        except (
            User.DoesNotExist,
            ValueError,
            json.JSONDecodeError,
            base64.binascii.Error,
        ):
            pass

        return None, False

    def get_user_preference(self, user):
        """
        Check if any of the user's notification settings have email notifications enabled.
        """
        return NotificationSetting.objects.filter(user=user, email=True).exists()

    def update_user_preferences(self, user, subscribe):
        """
        Update all of the user's notification settings to set email preference.
        """
        NotificationSetting.objects.filter(user=user).update(email=subscribe)
