from django.db.models import Q

from rest_framework.serializers import(
     ModelSerializer,
     EmailField,
     CharField,
     SerializerMethodField,
     BooleanField,
     NullBooleanField,
     Serializer,
     )
from django.contrib.auth import get_user_model

from rest_framework_jwt.settings import api_settings
from accounts.models import *

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

User = get_user_model()

# reset password
from . password_reset_form_api import MyPasswordResetForm

from django.conf import settings
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import APIException


class UserDetailSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile_number', 'country_code', 'is_mail_verify',
                  'is_num_verify']


class APIException400(APIException):
    status_code = 400



class UserLoginSerializer(ModelSerializer):
    device_token = CharField(required=True, error_messages={'required': 'device_token key is required', 'blank':'Device token is required'})
    device_type = CharField(required=True, error_messages={'required': 'device_type key is required', 'blank':'Device type is required'})
    # country_code = CharField(allow_blank=True, error_messages={'required': 'country_code key is required'})
    password = CharField(required=True, error_messages={'required': 'password key is required', 'blank':'Password is required'})
    mobile_or_email = CharField(required=True, error_messages={'required': 'mobile_or_email key is required', 'blank':'Mobile number or email is required'})
    token = CharField(allow_blank=True, read_only=True)
    login_type = CharField(allow_blank=True, read_only=True)
    user_id = CharField(allow_blank=True, read_only=True)

    def validate(self, data):
        user_obj = None
        mobile_or_email = data['mobile_or_email']
        device_token = data['device_token']
        device_type = data['device_type']
        # country_code = data['country_code']
        password = data['password']

        if mobile_or_email.isdigit() and not '@' in mobile_or_email:
            # check user by mobile number
            user = User.objects.filter(mobile_number=mobile_or_email,
                                    account_type='1').exclude(mobile_number__isnull=True,).exclude(mobile_number__iexact='').distinct()

            if user.exists() and user.count() == 1:
                # check mobile number is active or not
                user_obj = user.first()
                # if not user_obj.is_num_verify:
                login_type = 1  # by mobile
            else:
                APIException400({
                    'message': 'Invalid credentials',
                })
        else:
            # check user login by email
            user = User.objects.filter(email__iexact=mobile_or_email, account_type='1').exclude(email__isnull=True, ).exclude(email__iexact='').distinct()
            if user.exists() and user.count() == 1:
                # check email is active or not
                user_obj = user.first()
                # if not user_obj.is_mail_verify:
                login_type = 2  # by mail
            else:
                APIException400({
                    'message': 'Invalid credentials',
                })

        if user_obj:
            if not user_obj.is_active:
                raise APIException400("You account is currently blocked.")

            pass_passes = user_obj.check_password(password)
            if pass_passes:
                # To save device token
                user_obj.device_token = device_token
                user_obj.device_type = device_type
                user_obj.save()

                payload = jwt_payload_handler(user_obj)
                token = jwt_encode_handler(payload)
                data['token'] = 'JWT ' +token
                data['login_type'] = login_type
                data['user_id'] = user_obj.id
                return data
        raise APIException400({
            'message': 'Invalid credentials',
        })

    class Meta:
        model = User
        fields = ['mobile_or_email', 'user_id', 'login_type', 'password', 'token', 'device_token', 'device_type']

class UserCreateSerializer(Serializer):
    first_name = CharField(allow_blank=True, error_messages={'required': 'first name token key required'})
    last_name = CharField(allow_blank=True, error_messages={'required': 'last name key required'})
    email = EmailField(allow_blank=True, error_messages={'required': 'email key required'})
    mobile_number = CharField(allow_blank=True, error_messages={'required': 'mobile number key required'})
    country_code = CharField(allow_blank=True, error_messages={'required': 'country code key required'})
    profile_type = CharField(allow_blank=True, error_messages={'required': 'profile type key required'})
    password = CharField(allow_blank=True, error_messages={'required': 'password key required'})
    account_type = CharField(error_messages={'required': 'account type key required', 'blank':'account type is required'})
    social_id = CharField(allow_blank=True, error_messages={'required': 'social id key required'})
    device_token = CharField(error_messages={'required': 'device_token key is required' ,'blank': 'device token  is required'})
    device_type = CharField(error_messages={'required': 'device_type key is required','blank': 'device type is required'})

    def validate(self, data):
        mobile_number = data['mobile_number']
        password = data['password']
        device_type = data['device_type']
        country_code = data['country_code']
        email = data['email']
        account_type = data['account_type']
        social_id = data['social_id']
        profile_type = data['profile_type']
        first_name = data['first_name']
        last_name = data['last_name']

        # device type validation
        if device_type not in ['1', '2']:
            raise APIException400({
                'message': 'Please enter correct format of device_type',

            })

        if account_type == '1':
            # number validation
            if first_name == '':
                raise APIException400({
                    'message': 'First name is required',
                })

            if last_name == '':
                raise APIException400({
                    'message': 'Last name is required',
                })

            if mobile_number.isdigit():
                user_qs = User.objects.filter(mobile_number__iexact=mobile_number, country_code=country_code,
                                              account_type='1').exclude(mobile_number__isnull=True).exclude(mobile_number__iexact='').distinct()
                if user_qs.exists():
                    raise APIException400({
                        'message': 'User with this mobile number is already exists',
                    })

            else:
                raise APIException400({
                    'message': 'Please correct your mobile number',
                })

            # email validation
            user_qs = User.objects.filter(email__iexact=email, account_type='1')
            if user_qs.exists():
                raise APIException400({
                    'message': 'User with this Email already exists',
                })

            # pass validation
            if len(password) < 8:
                raise APIException400({
                    'message': 'Password must be at least 8 characters',
                })

            # profile type validation
            if profile_type not in ['1', '2']:
                raise APIException400({
                    'message': 'Please enter correct format of profile type',

                })

            return data

        elif account_type in ['2', '3', '4', '5', '6']:
            if social_id == '':
                raise APIException400({
                    'message': 'Please provide social id',
                })
            return data
        else:
            raise APIException400({
                'message': 'Please select right account type',
            })


class BasicInfoSerializer(Serializer):

    gender = CharField(error_messages={'required': 'gender key is required','blank': 'gender is required'})
    birth_date = CharField(error_messages={'required': 'birth_date  key is required', 'blank': 'birth date is required'})
    birth_date_privacy = CharField(error_messages={'required': 'birth_date_privacy key is required','blank':'Please select birth date privacy'})
    language = CharField(error_messages={'required': 'language key is required','blank': 'language is required'})
    nationality = CharField(error_messages={'required': 'nationality key is required','blank': 'nationality is required'})
    bio = CharField(allow_blank=True, error_messages={'required': 'bio key is required'})


class UserContactInfoSerializer(Serializer):

    current_city = CharField( allow_blank=True, error_messages={'required': 'current_city key is required'})
    current_city_lat = CharField( allow_blank=True, error_messages={'required': 'current_city_lat key is required'})
    current_city_long = CharField( allow_blank=True, error_messages={'required': 'current_city_long key is required'})
    current_city_privacy = CharField(allow_blank=True, error_messages={'required': 'current_city_privacy  key is required'})
    hometown = CharField(allow_blank=True, error_messages={'required': 'hometown key is required'})
    hometown_lat = CharField(allow_blank=True, error_messages={'required': 'hometown_lat key is required'})
    hometown_long = CharField(allow_blank=True, error_messages={'required': 'hometown_long key is required'})
    hometown_privacy = CharField(allow_blank=True, error_messages={'required': 'hometown_privacy key is required'})
    # ethnicity = serializers.ListField(child=serializers.CharField(), allow_empty=True, error_messages={'required': 'ethnicity key is required'})
    alt_mobile_number = CharField(allow_blank=True, error_messages={'required': 'alt_mobile_number key is required'})
    country_code = CharField(allow_blank=True, error_messages={'required': 'country_code key is required'})
    website_link = CharField(allow_blank=True, error_messages={'required': 'website_link key  is required'})


class UserEducationalDetailsSerializer(Serializer):

    college_name = CharField(allow_blank=True, error_messages={'required': 'college_name key is required'})
    college_since = CharField(allow_blank=True, error_messages={'required': 'college_since  key is required'})
    secondary_school = CharField(allow_blank=True, error_messages={'required': 'secondary_school key is required'})
    sec_class_year = CharField(allow_blank=True, error_messages={'required': 'sec_class_year key is required'})
    high_school = CharField(allow_blank=True, error_messages={'required': 'high_school key is required'})
    high_class_year = CharField(allow_blank=True, error_messages={'required': 'high_class_year key is required'})


class WorkExperienceSerializer(Serializer):

    company_name = CharField(allow_blank=True, error_messages={'required': 'company_name key is required'})
    job_title = CharField(allow_blank=True, error_messages={'required': 'job_title  key is required'})
    location = CharField(allow_blank=True, error_messages={'required': 'location key is required'})
    work_des = CharField(allow_blank=True, error_messages={'required': 'work_des key is required'})
    is_working_here = BooleanField(required=True, initial=False, error_messages={'required': 'is_working_here key is required'})
    working_since = CharField(allow_blank=True, error_messages={'required': 'working_since key is required'})
    location_lat = CharField(allow_blank=True, error_messages={'required': 'location_lat key is required'})
    location_long = CharField(allow_blank=True, error_messages={'required': 'location_long key is required'})


class UserPersonalSerializer(Serializer):

    political_view = CharField(allow_blank=True, error_messages={'required': 'political_view key is required'})
    world_view = CharField(allow_blank=True, error_messages={'required': 'world_view  key is required'})
    religious_view = CharField(allow_blank=True, error_messages={'required': 'religious_view key is required'})



class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """

    email = serializers.EmailField(error_messages={'required':'email key is required', 'blank': 'email is required'})

    class Meta:
        model = User
        fields = [

            'email',
        ]

    password_reset_form_class = MyPasswordResetForm

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(_('Error'))

        if not User.objects.filter(email=value, account_type ="1").exists():
            raise serializers.ValidationError(_('This e-mail address is not linked with any account'))

        return value

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }
        self.reset_form.save(**opts)


# class UserInterestSerializer(Serializer):
#     activities = serializers.ListField(child=serializers.CharField(), allow_empty=True, error_messages={'required': 'activities key is required'})
#     hobbies = serializers.ListField(child=serializers.CharField(), allow_empty=True, error_messages={'required': 'hobbies key is required'})
#     music = serializers.ListField(child=serializers.CharField(), allow_empty=True, error_messages={'required': 'music key is required'})
#     movies = serializers.ListField(child=serializers.CharField(), allow_empty=True, error_messages={'required': 'movies key is required'})
#     tv_shows = serializers.ListField(child=serializers.CharField(), allow_empty=True, error_messages={'required': 'tv_shows key is required'})
#     games = serializers.ListField(child=serializers.CharField(), allow_empty=True, error_messages={'required': 'games key is required'})


class UserInterestSerializer(Serializer):
    activities = CharField( allow_blank=True, error_messages={'required': 'activities key is required'})
    hobbies = CharField( allow_blank=True, error_messages={'required': 'hobbies key is required'})
    music = CharField( allow_blank=True, error_messages={'required': 'music key is required'})
    movies = CharField( allow_blank=True, error_messages={'required': 'movies key is required'})
    tv_shows = CharField( allow_blank=True, error_messages={'required': 'tv_shows key is required'})
    games = CharField(allow_blank=True, error_messages={'required': 'games key is required'})
    interest_text = CharField(allow_blank=True, error_messages={'required': 'interest_text key is required'})


class GetUserDetailSerializer(ModelSerializer):
    language = SerializerMethodField()

    def get_language(self, instance):
        language = instance.language.values_list('lang_name',flat=True).all()
        return language

    class Meta:
        model = User
        fields = [
            'profile_image',
            'gender',
            'birth_date',
            'birth_date_privacy',
            'language',
            'nationality',
            'bio',
        ]


class ViewProfileBasicInfoSerializer(ModelSerializer):
    gender = SerializerMethodField()

    def get_gender(self ,instance):
        return instance.get_gender_display()

    class Meta:
        model = User
        fields = [
            'gender',
            'birth_date',
            'nationality',
            'bio'
        ]


class SocialLinkSerializer(ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ['social_link_type','link']


class EthnicitySerializer(ModelSerializer):
    class Meta:
        model = Ethnicity
        fields = ['country_name' ,'flag']

class ViewProfileContactInfoSerializer(ModelSerializer):
    ethnicity = SerializerMethodField()
    social_link = SocialLinkSerializer(many=True)

    def get_ethnicity(self,instance):
        qs = instance.ethnicity.all()
        data = EthnicitySerializer(qs ,many=True).data
        return data

    class Meta:
        model = UserContactInfo
        fields = [
            'current_city',
            'current_city_privacy',
            'hometown',
            'hometown_privacy',
            'ethnicity',
            'alt_mobile_number',
            'country_code',
            'website_link',
            'social_link'
        ]


class ViewProfileUserInterestSerializer(ModelSerializer):
    class Meta:
        model = UserInterest
        fields = [
            'interest_text',
            'activities',
            'hobbies',
            'music',
            'movies',
            'tv_shows',
            'games'
        ]


class ViewProfileEducationDetailSerializer(ModelSerializer):
    class Meta:
        model = UserEducationalDetails
        fields = [
            'college_name',
            'college_since',
            'sec_class_year',
            'secondary_school',
            'high_school',
            'high_class_year'
        ]


class ViewProfileWorkDetailSerializer(ModelSerializer):
    class Meta:
        model = UserWorkExperience
        fields = [
            'company_name',
            'job_title',
            'location',
            'work_des',
            'working_since',
            'is_working_here'
        ]


class ViewProfileUserPersonalViewSerializer(ModelSerializer):
    class Meta:
        model = UserPersonalView
        fields = ['political_view', 'world_view', 'religious_view']


class UserProfileViewSerializer(ModelSerializer):
    basic_info = SerializerMethodField()
    contact_info = SerializerMethodField()
    interest = SerializerMethodField()
    education = SerializerMethodField()
    work = SerializerMethodField()
    personal_view = SerializerMethodField()

    def get_basic_info(self,instance):
        data = ViewProfileBasicInfoSerializer(instance).data
        return data

    def get_contact_info(self, instance):
        obj = UserContactInfo.objects.filter(user_id = instance)
        data = ViewProfileContactInfoSerializer(obj.first()).data
        return data

    def get_interest(self, instance):
        obj = UserInterest.objects.filter(user_id =instance)
        data = ViewProfileUserInterestSerializer(obj.first()).data
        return data

    def get_education(self, instance):
        obj = UserEducationalDetails.objects.filter(user_id=instance)

        data = ViewProfileEducationDetailSerializer(obj.first()).data
        return data

    def get_work(self, instance):
        obj = UserWorkExperience.objects.filter(user_id = instance)
        data = ViewProfileWorkDetailSerializer(obj.first()).data
        return data

    def get_work(self, instance):
        obj = UserWorkExperience.objects.filter(user_id = instance)
        data = ViewProfileWorkDetailSerializer(obj.first()).data
        return data

    def get_personal_view(self, instance):
        obj = UserPersonalView.objects.filter(user_id = instance)
        data = ViewProfileUserPersonalViewSerializer(obj.first()).data
        return data


    class Meta:
        model = User
        fields = [
            'basic_info',
            'contact_info',
            'interest',
            'education',
            'work',
            'personal_view'
        ]


class GetAllUserDataSerializer(ModelSerializer):
    post_count = SerializerMethodField()
    viewers_count = SerializerMethodField()
    viewing_count = SerializerMethodField()
    viewed_by = SerializerMethodField()
    social_link = SerializerMethodField()
    posts = SerializerMethodField()

    def get_post_count(self, instance):
        return 0

    def get_viewers_count(self, instance):
        count = ViewingAndViewers.objects.filter(viewed_to = instance, status ='2').count()
        return count
    def get_viewing_count(selfself, instance):
        count = ViewingAndViewers.objects.filter(viewed_by=instance, status='2').count()
        return count

    def get_viewed_by(self, instance):
        viewed_by = ViewingAndViewers.objects.filter(viewed_to=instance, status='2').values_list('viewed_by__first_name', flat=True)
        return viewed_by

    def get_social_link(self, instance):
        obj = UserContactInfo.objects.filter(user_id = instance).first()
        if obj:
            social_qs = obj.social_link.all()
            data = SocialLinkSerializer(social_qs,many=True).data
            return data
        else:
            return []


    def get_posts(self, instance):
        return []

    class Meta:
        model = User
        fields = [
            'profile_image',
            'first_name',
            'last_name',
            'post_count',
            'viewers_count',
            'viewing_count',
            'birth_date',
            'gender',
            'nationality',
            'profile_views_count',
            'bio',
            'viewed_by',
            'social_link',
            'posts',
        ]

class FollowAndUnfollowSerializer(Serializer):
        user_id = CharField(error_messages={'required': 'user_id key is required', 'blank': 'user id is required'})
        status = CharField(error_messages={'required': 'status  key is required', 'blank': 'status is required'})
