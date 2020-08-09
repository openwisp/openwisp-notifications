from django.http import HttpResponseRedirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import (
    GenericAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from openwisp_notifications.api.serializers import (
    NotificationListSerializer,
    NotificationSerializer,
    NotificationSettingSerializer,
)
from openwisp_notifications.handlers import clear_notification_cache
from openwisp_notifications.swapper import load_model
from openwisp_users.api.authentication import BearerAuthentication

UNAUTHORIZED_STATUS_CODES = (
    status.HTTP_401_UNAUTHORIZED,
    status.HTTP_403_FORBIDDEN,
)

Notification = load_model('Notification')
NotificationSetting = load_model('NotificationSetting')


class NotificationPaginator(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class BaseNotificationView(GenericAPIView):
    model = Notification
    authentication_classes = [BearerAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()

    def get_queryset(self):
        return self.queryset.filter(recipient=self.request.user)


class NotificationListView(BaseNotificationView, ListModelMixin):
    serializer_class = NotificationListSerializer
    pagination_class = NotificationPaginator
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['unread']

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class NotificationDetailView(BaseNotificationView, RetrieveDestroyAPIView):
    serializer_class = NotificationSerializer
    lookup_field = 'pk'

    def patch(self, request, *args, **kwargs):
        return self._mark_notification_read()

    def _mark_notification_read(self):
        notification = self.get_object()
        notification.mark_as_read()
        return Response(status=status.HTTP_200_OK,)


class NotificationReadRedirect(BaseNotificationView):
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.mark_as_read()
        return HttpResponseRedirect(notification.target_url)

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        if response.status_code not in UNAUTHORIZED_STATUS_CODES:
            return response

        redirect_url = '{admin_login}?next={path}'.format(
            admin_login=reverse('admin:login'), path=self.request.path
        )
        return HttpResponseRedirect(redirect_url)


class NotificationReadAllView(BaseNotificationView):
    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.update(unread=False)
        # update() does not create post_save signal
        clear_notification_cache(sender=self, instance=queryset.first())
        return Response(status=status.HTTP_200_OK)


class BaseNotificationSettingView(GenericAPIView):
    model = NotificationSetting
    serializer_class = NotificationSettingSerializer
    authentication_classes = [BearerAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationSetting.objects.filter(user=self.request.user)


class NotificationSettingListView(BaseNotificationSettingView, ListModelMixin):
    pagination_class = NotificationPaginator
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['organization', 'type']

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class NotificationSettingView(BaseNotificationSettingView, RetrieveUpdateAPIView):
    lookup_field = 'pk'


notifications_list = NotificationListView.as_view()
notification_detail = NotificationDetailView.as_view()
notifications_read_all = NotificationReadAllView.as_view()
notification_read_redirect = NotificationReadRedirect.as_view()
notification_setting_list = NotificationSettingListView.as_view()
notification_setting = NotificationSettingView.as_view()
