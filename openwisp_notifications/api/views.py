from django_filters.rest_framework import DjangoFilterBackend
from openwisp_notifications.api.serializers import (
    NotificationListSerializer,
    NotificationSerializer,
)
from openwisp_notifications.swapper import load_model
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import GenericAPIView, RetrieveDestroyAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from openwisp_users.api.authentication import BearerAuthentication

Notification = load_model('Notification')


class NotificationPaginator(PageNumberPagination):
    page_size = 10
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

    def patch(self, request, pk):
        return self._mark_notification_read(pk)

    def _mark_notification_read(self, notification_id):
        notification = self.get_object()
        notification.mark_as_read()
        return Response(status=status.HTTP_200_OK,)


class NotificationReadAllView(BaseNotificationView):
    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.update(unread=False)
        Notification.invalidate_cache(request.user)
        return Response(status=status.HTTP_200_OK)


notifications_list = NotificationListView.as_view()
notification_detail = NotificationDetailView.as_view()
notifications_read_all = NotificationReadAllView.as_view()
