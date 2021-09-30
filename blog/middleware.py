from django.views.generic.base import View
from .models import ViewsMid


class ViewsMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        remote_addr = request.META.get("REMOTE_ADDR")
        ua = request.META.get("HTTP_USER_AGENT")

        if x_forwarded_for:
            ip = x_forwarded_for
        elif remote_addr:
            ip = remote_addr
        else:
            ip = '127.0.0.1'

        # ip_address = ViewsMid.objects.get_or_create(ip_addr=ip, ua=ua,)
        try:
            ip_address = ViewsMid.objects.get(ip_addr=ip)
        except ViewsMid.DoesNotExist:
            ip_address = ViewsMid.objects.create(ip_addr=ip, ua=ua)
        request.user.ip_address = ip_address
        request.user.ua = ua

        response = self.get_response(request)
        return response
