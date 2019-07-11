from rest_framework.generics import (
		CreateAPIView,
	)
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from accounts.models import *
import random
from django.core import mail
from django.db.models import F

from authy.api import AuthyApiClient
authy_api = AuthyApiClient('MG90955d0e460f3ca2f60f08f45d6f4e85')

User = get_user_model()

# base64 to image
import base64
from django.core.files.base import ContentFile

# PASSWORD RESET BY EMAIL START------

from .settings import (
	PasswordResetSerializer,
)
from rest_framework_jwt.settings import api_settings
from django.contrib.sites.shortcuts import get_current_site

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


from rest_framework.generics import GenericAPIView
from rest_framework import status

# END--------------------------------

from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from . password_reset_form import MyPasswordResetForm

# send email verify email
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from accounts.api.tokens import account_activation_token
import datetime


class UserLoginAPIView(APIView):
	def post(self, request):
		data = request.data
		serializer = UserLoginSerializer(data=data)
		if serializer.is_valid():
			user_data = serializer.data
			user = User.objects.get(id=user_data['user_id'])

			if user_data['login_type'] == '1':  # mobile login
				if not user.is_num_verify:
					# send otp to verify number

					# authy_api.phones.verification_start(data['mobile_number'], data['country_code'],
					# 	via='sms', locale='en')

					return Response({
						'message': 'Please verify your number',
						'data': user_data
					}, status=200)

				user_all_data = UserDetailSerializer(user).data
				user_all_data['token'] = user_data['token']
				user_all_data['login_type'] = user_data['login_type']

				return Response({
					'message': 'Login successfully',
					'data': user_all_data
				}, status=200)

			elif user_data['login_type'] == '2':
				if not user.is_mail_verify:
					## send email verification

					current_site = get_current_site(request)
					site_name = current_site.name
					domain = current_site.domain

					to = request.data['mobile_or_email']
					plain_message = None
					from_email = 'Viewed <webmaster@localhost>'
					subject = 'Activate Your Viewed Account'
					message_text = render_to_string('account_activation/account_activation_email.html', {
						'user': user,
						'domain': domain,
						'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
						'token': account_activation_token.make_token(user),
					})
					mail.send_mail(subject, plain_message, from_email, [to], html_message=message_text)

					return Response({
						'message': "Please verify your email before login",
						'data': {}
					}, status=400)

				user_all_data = UserDetailSerializer(user).data
				user_all_data['token'] = user_data['token']
				user_all_data['login_type'] = user_data['login_type']

				return Response({
					'message': 'Login successfully',
					'data': user_all_data
				}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message':error_msg[0]}, status = 400)
		return Response(serializer.errors, status=400)


class UserCreateAPIView(CreateAPIView):
	serializer_class = UserCreateSerializer
	def create(self, request, *args, **kwargs):

		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			data = serializer.data

			if data['account_type'] == '1':  # normal signup

				username = data['first_name'] + '-' + data['last_name'] + '-' + str(random.randint(100000, 10000000))
				user_obj = User.objects.create(username=username, email=data['email'], first_name=data['first_name'], last_name=data['last_name'],
									country_code=data['country_code'], mobile_number=data['mobile_number'], profile_type=data['profile_type'],
									device_type=data['device_type'], device_token=data['device_token'])
				user_obj.set_password(data['password'])
				user_obj.save()
				message = 'Sign-up successfully. Please verify Your mobile number'

				# send email verification mail

				current_site = get_current_site(request)
				site_name = current_site.name
				domain = current_site.domain
				# use_https =False
				# extra_email_context = None
				#
				# context = {
				# 	'domain': domain,
				# 	'user':user_obj,
				# 	'site_name': site_name,
				# 	'protocol': 'https' if use_https else 'http',
                # 				**(extra_email_context or {}),
				# 	'uid': urlsafe_base64_encode(force_bytes(user_obj.pk)).decode('utf-8'),
				# 	'token': account_activation_token.make_token(user_obj),
				# }
				# subject_template_name = 'account_activation/subject.txt',
				# email_template_name = 'account_activation/account_activation_email.html'

				# html_email_template_name=None
				# MyPasswordResetForm.send_mail(subject_template_name, email_template_name, context,
				#
				# 							  from_email,email,html_email_template_name)
				#


				subject = 'Activate Your Viewed Account'
				to = data['email']
				plain_message =None
				from_email = 'Viewed <webmaster@localhost>'
				message_text = render_to_string('account_activation/account_activation_email.html', {
					'user': user_obj,
					'domain': domain,
					'uid': urlsafe_base64_encode(force_bytes(user_obj.pk)).decode(),
					'token': account_activation_token.make_token(user_obj),
				})
				mail.send_mail(subject, plain_message, from_email, [to], html_message=message_text)

				# send mobile number verification otp

				mobile_number = data.get("mobile_number")
				country_code = data.get("country_code")
				# request = authy_api.phones.verification_start(mobile_number, country_code,
				# 									via='sms', locale='en')
				# if request.content['success'] == True:
				# 	return Response(
				# 		serializer.data,
				# 		status=200)
				# else:
				# 	return Response({
				# 	  'success':"false",
				# 	  'msg':request.content['message']},
				# 	  status=200)


			else:  # social signup or login
				user_qs = User.objects.filter(social_id=data['social_id'], account_type=data['account_type']).exclude(social_id__isnull=True).exclude(social_id__iexact='').distinct()
				if user_qs.exists():
					user_obj = user_qs.first()
					message = 'Successfully logged in'
				else:
					username = data['social_id'] + '-' + data['account_type']
					password = data['social_id']
					user_obj = User.objects.create(username=username, email=data['email'], first_name=data['first_name'],
										last_name=data['last_name'], country_code=data['country_code'], mobile_number=data['mobile_number'],
										profile_type=data['profile_type'], device_type=data['device_type'],
										device_token=data['device_token'], account_type=data['account_type'], social_id=data['social_id'])
					user_obj.set_password(password)
					user_obj.save()
					message = 'Sign-up successfully'

			user_data = UserDetailSerializer(user_obj).data
			payload = jwt_payload_handler(user_obj)
			token = jwt_encode_handler(payload)
			user_data['token'] = 'JWT ' + token

			return Response({
					'message': message,
					'data': user_data
				}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class UserBasicInfoAPIView(APIView):
	"""
	get create and update user basic info
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		data = request.data
		serializer = BasicInfoSerializer(data=data)
		if serializer.is_valid():

			data = serializer.data
			user = request.user
			user.gender = data['gender']
			user.birth_date = data['birth_date']
			user.birth_date_privacy= data['birth_date_privacy']

			user.nationality = data['nationality']
			user.bio = data['bio']
			if request.FILES.get('profile_image') is not None:
				user.profile_image = request.FILES.get('profile_image')
			user.save()

			# getting lang in list format
			lang_list = dict(request.data).get('language')
			# delete linked language
			user.language.all().delete()
			lang_qs = []
			for lang in lang_list:
				lang_obj = Languages.objects.create(lang_name = lang)
				lang_qs.append(lang_obj)
			user.language.add(*lang_qs)
			return Response({
				'message': 'Basic info updated successfully'
			},status=200)
		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)

	def get(self, request):
		user = request.user
		data = GetUserDetailSerializer(user).data

		return Response({
			'data':data
		},200)


def base64_to_image(data):
	"""
	to convert base64 to image
	"""
	format, imgstr = data.split(';base64,')
	ext = format.split('/')[-1]
	image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)  # You can save this as file instance.
	return image


class UserContactInfoAPIView(APIView):
	"""
	get create and update user contact info
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		qs = UserContactInfo.objects.filter(user_id =request.user)
		data = ViewProfileContactInfoSerializer(qs.first()).data
		return Response({
			'data': data
		}, 200)

	def post(self, request):
		data = request.data
		serializer = UserContactInfoSerializer(data=data)
		if data.get('social_link') is None:
			return Response({
				'message': 'social_link key is required'
			}, 400)
		if data.get('ethnicity') is None:
			return Response({
				'message': 'ethnicity key is required'
			}, 400)
		if serializer.is_valid():
			contact_qs = UserContactInfo.objects.filter(user_id=request.user)
			ethnicity_list = dict(request.data).get('ethnicity')
			if contact_qs.exists():
				contact_obj = contact_qs.first()
				contact_obj.current_city = data['current_city']
				contact_obj.current_city_lat = data['current_city_lat']
				contact_obj.current_city_long = data['current_city_long']
				contact_obj.hometown = data['hometown']
				contact_obj.hometown_lat = data['hometown_lat']
				contact_obj.hometown_long = data['hometown_long']
				contact_obj.alt_mobile_number=data['alt_mobile_number']
				contact_obj.website_link = data['website_link']
				contact_obj.country_code = data['country_code']
				contact_obj.hometown_privacy = data['hometown_privacy']
				contact_obj.current_city_privacy=data['current_city_privacy']
				contact_obj.save()

				# delete linked language
				contact_obj.ethnicity.all().delete()
				ethnicity_qs = []
				for ethnicity in ethnicity_list:

					ethnicity_obj = Ethnicity.objects.create(country_name=ethnicity['country_name'], flag= base64_to_image(ethnicity['flag']))
					ethnicity_qs.append(ethnicity_obj)
				contact_obj.ethnicity.add(*ethnicity_qs)

				# delete relations
				SocialLink.objects.filter(id__in = contact_obj.social_link.all()).delete()

				# add new relations
				if not data.get('social_link') == []:

					social_link_qs =[]
					for link in data['social_link']:
						social_link_obj = SocialLink.objects.create(social_link_type=link['social_link_type'],link=link['link'])
						social_link_qs.append(social_link_obj)
					contact_obj.social_link.add(*social_link_qs)

				return Response({
					'message': 'Contact Info updated successfully'
				}, status=200)

			obj = UserContactInfo.objects.create(user_id=request.user, current_city=data['current_city'], current_city_privacy=data['current_city_privacy'],
										hometown=data['hometown'], hometown_privacy=data['hometown_privacy'],
										alt_mobile_number=data['alt_mobile_number'], country_code=data['country_code'],
										website_link=data['website_link'])

			ethnicity_qs = []
			for ethnicity in ethnicity_list:
				ethnicity_obj = Ethnicity.objects.create(country_name=ethnicity['country_name'], flag= base64_to_image(ethnicity['flag']))
				ethnicity_qs.append(ethnicity_obj)
			obj.ethnicity.add(*ethnicity_qs)

			if not data.get('social_link') == []:

				social_link_qs = []
				for link in data['social_link']:
					social_link_obj = SocialLink.objects.create(social_link_type=link['social_link_type'],
																link=link['link'])
					social_link_qs.append(social_link_obj)
				obj.social_link.add(*social_link_qs)

			return Response({
				'message': 'Contact Info updated successfully'
			}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class UserEducationalDetailsAPIView(APIView):
	"""
	get create and update user educational detail
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		qs = UserEducationalDetails.objects.filter(user_id =request.user)
		data = ViewProfileEducationDetailSerializer(qs.first()).data
		return Response({
			'data': data
		}, 200)

	def post(self, request):
		data = request.data
		serializer = UserEducationalDetailsSerializer(data=data)
		if serializer.is_valid():
			edu_qs = UserEducationalDetails.objects.filter(user_id=request.user)
			if edu_qs.exists():
				edu_obj = edu_qs.first()
				edu_obj.college_name=data['college_name']
				edu_obj.sec_class_year=data['sec_class_year']
				edu_obj.high_class_year=data['high_class_year']
				edu_obj.high_school=data['high_school']
				edu_obj.secondary_school=data['secondary_school']
				edu_obj.college_since=data['college_since']
				edu_obj.save()

				return Response({
					'message': 'Educational detail updated successfully'
				}, status=200)

			UserEducationalDetails.objects.create( user_id=request.user, college_name=data['college_name'], college_since=data['college_since'], secondary_school=data['secondary_school'],
												   sec_class_year=data['sec_class_year'], high_school=data['high_school'],
												   high_class_year=data['high_class_year'])

			return Response({
				'message': 'Educational detail updated successfully'
			}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class UserWorkExperienceAPIView(APIView):
	"""
	get create and update work  detail
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		qs = UserWorkExperience.objects.filter(user_id = request.user)
		data = ViewProfileWorkDetailSerializer(qs.first()).data
		return Response({
			'data': data
		}, 200)

	def post(self, request):
		data = request.data
		serializer = WorkExperienceSerializer(data=data)
		if serializer.is_valid():
			work_qs = UserWorkExperience.objects.filter(user_id=request.user)
			if work_qs.exists():
				work_qs = work_qs.first()
				work_qs.company_name = data['company_name']
				work_qs.job_title = data['job_title']
				work_qs.location = data['location']
				work_qs.location_lat = data.get('location_lat')
				work_qs.location_long = data.get('location_long')
				work_qs.work_des = data['work_des']
				work_qs.working_since = data['working_since']
				work_qs.is_working_here = data['is_working_here'].capitalize()
				work_qs.save()

				return Response({
					'message': 'Work experience updated successfully'
				}, status=200)

			UserWorkExperience.objects.create(user_id=request.user, company_name=data['company_name'],
											  job_title=data['job_title'], location=data['location'],location_long = data.get('location_long'),
											  location_lat = data.get('location_lat') ,work_des=data['work_des'], is_working_here=data['is_working_here'].capitalize(),
											  working_since=data['working_since'])

			return Response({
				'message': 'Work experience updated successfully'
			}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class UserPersonalViewAPIView(APIView):
	"""
	get create and update user personal view
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		qs = UserPersonalView.objects.filter(user_id =request.user)
		data = ViewProfileUserPersonalViewSerializer(qs.first()).data
		return Response({
			'data': data
		}, 200)

	def post(self, request):
		data = request.data
		serializer = UserPersonalSerializer(data=data)
		if serializer.is_valid():
			per_qs = UserPersonalView.objects.filter(user_id = request.user)
			if per_qs.exists():
				per_obj = per_qs.first()
				per_obj.political_view=data['political_view']
				per_obj.world_view=data['world_view']
				per_obj.religious_view=data['religious_view']
				per_obj.save()

				return Response({
					'message': 'User personal view updated successfully'
				}, status=200)

			UserPersonalView.objects.create(user_id=request.user, political_view=data['political_view'],
											world_view=data['world_view'], religious_view=data['religious_view'])

			return Response({
				'message': 'User personal view updated successfully'
			}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


def make_obj(interest_list, user, interest_type, interest):
	interest_obj = [UserInterests(user_id=user, interest_type=interest_type, interest=activitie) for activitie
					in interest]
	interest_list.extend(interest_obj)


class UserInterestsAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]


	def get(self, request):
		qs = UserInterest.objects.filter(user_id = request.user)
		data = ViewProfileUserInterestSerializer(qs.first()).data
		return Response({
			'data': data

		}, 200)

	def post(self, request):
		serializer = UserInterestSerializer(data=request.data)
		if serializer.is_valid():
			data = serializer.data
			user = request.user
			int_qs = UserInterest.objects.filter(user_id=request.user)
			if int_qs.exists():
				int_obj = int_qs.first()
				int_obj.activities = data['activities']
				int_obj.hobbies = data['hobbies']
				int_obj.tv_shows = data['tv_shows']
				int_obj.games = data['games']
				int_obj.movies = data['movies']
				int_obj.music = data['music']
				int_obj.interest_text = data['interest_text']
				int_obj.save()

				return Response({
					'message': 'User Interest updated successfully'
				}, status=200)

			UserInterest.objects.create(user_id= user, activities=data['activities'],
										 hobbies=data['hobbies'], music=data['music'], movies=data['movies'],
										 tv_shows=data['tv_shows'], games=data['games'],interest_text=data['interest_text'])


			# interest_list = []
			#
			# interest = ['activities', 'hobbies', 'music', 'movies', 'tv_shows', 'games']
			# for i in range(6):
			# 	make_obj(interest_list,request.user, i+1, data[interest[i]])
			#
			# UserInterests.objects.bulk_create(interest_list)

			# updated user interest after demand

			return Response({
				'message': 'User Interest updated successfully'
			}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class PasswordResetView(GenericAPIView):
	"""
	Calls Django Auth PasswordResetForm save method.
	Accepts the following POST parameters: email
	Returns the success/fail message.
	"""
	serializer_class = PasswordResetSerializer

	def post(self, request):
		# Create a serializer with request.data
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			# Return the success message with OK HTTP status
			return Response(
				{
				'message':"Password reset e-mail has been sent successfully"
				}, 200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class UserPhoneVerifyAfterRegisterAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		data = request.data
		user = request.user
		mobile_number = data.get('mobile_number')
		country_code = data.get('country_code')
		verification_code = data.get('verification_code')
		if mobile_number and country_code and verification_code:
			# check = authy_api.phones.verification_check(mobile_number, country_code, verification_code)
			# if check.ok() == True or verification_code == "1234":
			if verification_code == "1234":
				user.is_num_verify = True
				user.save()
				return Response({
					# 'message':check.content['message']},
					'message': 'Your number has been verified successfully'
				}, status=200)

			return Response({
				# 'message':check.content['message']
				'message': 'verification code is incorrect'
			}, status=400)

		return Response({
			'message': 'Please provide data in valid format'
		}, status=400)


class OTPReSendForPhoneVerify(APIView):

	def post(self, request):
		mobile_number = request.data.get('mobile_number')
		country_code = request.data.get('country_code')
		if mobile_number and country_code:
			try:
				# authy_api.phones.verification_start(phone_number, country_code,
				# 											  via='sms', locale='en')
				return Response({
						'message': 'Otp sent successfully'},
						status=200)

			except:
				return Response({
					'message': 'Otp sent successfully'},
					status=200)

		return Response({
				'message': 'Please provide data in valid format'
			}, status=400)


class ViewUserProile(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		user = request.user
		data = UserProfileViewSerializer(user).data
		return Response({
			'data': data
		})


class GetAllUserData(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		data = GetAllUserDataSerializer(request.user).data
		return Response({
			'data': data
		})

from collections import Counter
from django.db.models import Count

class GetViewingListApiView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		qs = ViewingAndViewers.objects.filter(viewed_by=request.user, status="2").values(first_name=F('viewed_to__first_name'),
				last_name=F('viewed_to__last_name'),profile_image=F('viewed_to__profile_image'),
				user_id=F('viewed_to__id'))

		viewers_list= Counter(ViewingAndViewers.objects.filter(status='2').values_list('viewed_to',flat=True))
		for obj in qs:
			if obj['user_id'] in viewers_list:
				obj['viewed_by'] =viewers_list[obj['user_id']]
			else:
				obj['viewed_by']=0
		return Response({
			'data':qs,
		}, 200)

class GetAllVewersListApiView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self,request):
		qs = ViewingAndViewers.objects.filter(viewed_to = request.user, status="2").values(first_name=F('viewed_by__first_name'),
				last_name=F('viewed_by__last_name'), profile_image=F('viewed_by__profile_image'),
				user_id=F('viewed_by__id'))
		viewers_list= Counter(ViewingAndViewers.objects.filter(status='2').values_list('viewed_to',flat=True))
		for obj in qs:
			if obj['user_id'] in viewers_list:
				obj['viewed_by'] =viewers_list[obj['user_id']]
			else:
				obj['viewed_by']=0
		return Response({
			'data': qs,
		}, 200)

# class FollowAndUnfollowApiView(APIView):
# 	permission_classes = (IsAuthenticated,)
# 	authentication_classes = [JSONWebTokenAuthentication]
# 	def post(self,request):
# 		data =request.data
# 		serializer = FollowAndUnfollowSerializer(data=data)
# 		if serializer.is_valid():
# 			if data['status']=='1':
# 				ViewingAndViewers.objects.create(viewed_by=request.user, viewed_to__id=data['user_id'], status="")
# 			elif data['status'] == '2':
#
# 			else:
# 				return Response({
#
# 				},400)
#
#
# 		error_keys = list(serializer.errors.keys())
# 		if error_keys:
# 			error_msg = serializer.errors[error_keys[0]]
# 			return Response({'message': error_msg[0]}, status=400)
# 		return Response(serializer.errors, status=400)
