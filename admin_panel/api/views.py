
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny,IsAuthenticated
from .serializers import *
from admin_panel.models import *

from authy.api import AuthyApiClient
authy_api = AuthyApiClient('YnWJyrBePlU7U4Xj892WLAYeuEuaSsrH')

User = get_user_model()


class UserBlockAPIView(APIView):
    def post(self,request,*args,**kwargs):
        user_id = self.kwargs['user_id']

        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({
                'message': 'No user to block'},
                status=400)

        user.is_active = False
        user.save()

        return Response({

            'message': 'Blocked successfully'},
            status=200)


class UserUnblockAPIView(APIView):
    def post(self,request,*args,**kwargs):
        user_id = self.kwargs['user_id']
        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({
                'message': 'No user to unblock'},
                status=400)
        user.is_active = True
        user.save()
        return Response({
            'message': 'Unblocked successfully'},
            status=200)


class UserDeleteAPIView(APIView):
    def post(self,request,*args,**kwargs):
        user_id = self.kwargs['user_id']
        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({
                'message': 'No user to delete'},
                status=400)
        user.delete()
        return Response({

            'message': 'deleted successfully'},
            status=200)


class FAQDeleteAPIView(APIView):

    def delete(self, request, *args, **kwargs):

        try:
            Faq.objects.get(id=self.kwargs.get('faq_id')).delete()
        except:
            return Response({

                'message': 'Somthing went wrong. Please try after some time'
            }, status=500)

        return Response({

            'message': 'Deleted Successfully'
        }, status=200)

