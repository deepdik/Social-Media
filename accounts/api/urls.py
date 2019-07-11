from django.urls import path

from .views import *


urlpatterns = [

    path('login', UserLoginAPIView.as_view(), name="login"),
    path('registration', UserCreateAPIView.as_view(), name='registration'),
    path('password_reset', PasswordResetView.as_view(), name='rest_password_reset'),
    path('user_basic_info', UserBasicInfoAPIView.as_view(), name='user_basic_info'),
    path('user_contact_info', UserContactInfoAPIView.as_view(), name='user_contact_info'),
    path('user_educational_detail', UserEducationalDetailsAPIView.as_view(), name='user_educational_detail'),
    path('user_work_experience', UserWorkExperienceAPIView.as_view(), name='user_work_experience'),
    path('user_interest', UserInterestsAPIView.as_view(), name='user_interest'),

    path('user_personal_view', UserPersonalViewAPIView.as_view(), name='user_personal_view'),
    path('otp_varify', UserPhoneVerifyAfterRegisterAPIView.as_view(), name="otp_varify"),
    path('otp_re_generate', OTPReSendForPhoneVerify.as_view(), name="otp_re_generate"),

    path('view_profile', ViewUserProile.as_view(), name="view_profile"),

    path('get_all_user_data', GetAllUserData.as_view(), name="view_profile"),

    path('viewing_list', GetViewingListApiView.as_view(), name="viewing_list"),
    path('viewers_list', GetAllVewersListApiView.as_view(), name="viewers_list"),

]