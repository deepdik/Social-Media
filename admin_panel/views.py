from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
import datetime
# Create your views here.
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.models import *
from .forms import *
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login ,logout
from django.utils.decorators import method_decorator

from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from accounts.api.password_reset_form import MyPasswordResetForm
from accounts.models import *
from .models import *
from django.shortcuts import get_object_or_404
from django.db.models import Sum



class AdminLoginView(View):
	def get(self, request):
		form = LoginForm
		if request.user.is_authenticated:
			return HttpResponseRedirect('/admin/panel/home/')

		return render(request, 'admin_panel/accounts/login.html', {'form': form})

	def post(self, request):
		form = LoginForm(request.POST or None)
		if form.is_valid():
			user = User.objects.get(email=request.POST['email'],account_type="1", is_staff=True, is_superuser=True,)
			login(request, user)
			return HttpResponseRedirect('/admin/panel/home')

		return render(request, 'admin_panel/accounts/login.html', {'form': form})


class LogoutView(View):

	def get(self,request):
		logout(request)
		return HttpResponseRedirect('/admin/panel/login/')


class ResetPasswordView(auth_views.PasswordResetView):
	 form_class = MyPasswordResetForm

from django.contrib.auth import update_session_auth_hash

class ChangePasswordView(View):

	def get(self, request):
		form = ChangePasswordForm(user=request.user)
		return render(request, 'admin_panel/accounts/change_password.html', {'form': form})

	def post(self, request):
		user = request.user
		print(request.POST)
		form = ChangePasswordForm(request.POST or None, user=request.user)

		if form.is_valid():
			password = form.cleaned_data['password']
			user.set_password(password)
			user.save()
			update_session_auth_hash(request, form.user)
			# messages.success(request, 'Your password have been changed successfully. Please login again to access account')
			return HttpResponseRedirect('/admin/panel/login/')
		return render(request, 'admin_panel/accounts/change_password.html', {'form': form})


class AdminHomeView(View):

	def get(self, request):
		user = request.user
		print(user)
		context = {
			'home': 'home'

		}
		return render(request, 'admin_panel/home.html', context)


class AdminProfileView(View):

	def get(self, request):

		form = AdminProfileEditForm
		user =request.user
		context = {

			'form': form,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'email': user.email,
			'mobile_number': user.mobile_number,
			'profile_image': user.profile_image,
			'cover_image': user.cover_image,
			'country_code': user.country_code
		}

		return render(request, 'admin_panel/accounts/admin_profile.html', context)


class AdminProfileEditView(View):
	def get(self, request):
		form = AdminProfileEditForm
		user = request.user
		context = {

			'form': form,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'email': user.email,
			'mobile_number': user.mobile_number,
			'profile_image': user.profile_image,
			'cover_image': user.cover_image,
			'country_code': user.country_code
		}

		return render(request, 'admin_panel/accounts/admin_profile_change.html', context)

	def post(self, request):
		data = request.POST
		user = request.user
		form = AdminProfileEditForm(request.POST or None, user=request.user)
		if form.is_valid():


			profile_image = request.FILES.get('profile_image')
			cover_image = request.FILES.get('cover_image')

			user.email = form.cleaned_data['email']
			user.first_name = form.cleaned_data['first_name']
			user.last_name = form.cleaned_data['last_name']
			user.mobile_number = form.cleaned_data['mobile_number']

			if profile_image is not None:
				user.profile_image = profile_image
			if cover_image is not None:
				user.cover_image = cover_image

			user.save()
			return HttpResponseRedirect('/admin/panel/admin_profile/')

		context = {

			'form': form,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'email': user.email,
			'mobile_number': user.mobile_number,
			'profile_image': user.profile_image,
			'cover_image': user.cover_image,
			'country_code': user.country_code
		}
		return render(request, 'admin_panel/accounts/admin_profile_change.html', context)


class UserListView(View):
	def get(self, request):
		users = User.objects.filter(is_staff=False).order_by('-date_joined')
		context = {

		'users':users,
		'sort_by': "default"

		}
		return render(request, 'admin_panel/account_management/user_list.html', context)


class UserdetailView(View):
	def get(self, request, *args, **kwargs):

		profile_id = self.kwargs['profile_id']
		user  = User.objects.prefetch_related('language').get(pk=profile_id)
		personal_view = UserPersonalView.objects.filter(user_id=user)
		education = UserEducationalDetails.objects.filter(user_id=user)
		contact_info = UserContactInfo.objects.filter(user_id=user).prefetch_related('social_link','ethnicity')
		work = UserWorkExperience.objects.filter(user_id=user)
		interest = UserInterest.objects.filter(user_id=user)
		context = {

		'userdata':user,
		'personal_view':personal_view,
		'education':education,
		'contact_info':contact_info,
		'work':work,
		'interest':interest

		}

		return render(request, 'admin_panel/account_management/userprofile.html', context)


class UserDateFilterView(View):
	def get(self, request):
		print(request.GET)

		start_date = datetime.datetime.strptime(request.GET.get('startdate'), '%m/%d/%Y').strftime('%Y-%m-%d')

		end_date = datetime.datetime.strptime(request.GET.get('enddate'), '%m/%d/%Y').strftime('%Y-%m-%d')

		filterdata = User.objects.filter(date_joined__range=(start_date, end_date), is_staff=False)
		context = {'users': filterdata, 'startdate' : request.GET.get('startdate'), 'enddate':request.GET.get('enddate'),'sort_by': 'dafault'}
		return render(request, 'admin_panel/account_management/user_list.html', context)


class UserSortView(View):
	def post(self, request):

		data = request.POST['sort_by']

		if data=="default":
			return HttpResponseRedirect('/admin/panel/account_management/')

		filterdata = User.objects.filter(is_staff=False).order_by(data)

		context = {'users': filterdata,
				   'sort_by': data
				   }
		return render(request, 'admin_panel/account_management/user_list.html', context)

	def get(self, request):
		return HttpResponseRedirect('/admin/panel/account_management/')


class TermsAboutContactView(View):

	def get(self, request, *args, **kwargs):

		obj = ContactAboutTerms.objects.all().first()

		if obj:
			about_us = obj.about_us
			terms = obj.terms
			contact_us = obj.contact_us
			id = obj.id
		else:
			about_us = ''
			terms = ''
			contact_us = ''
			id = None

		context = {
			'about_us': about_us,
			'terms': terms,
			'contact_us': contact_us,
			'id': id
		}
		return render(request, 'admin_panel/settings_management/terms_about_contact.html', context)

	def post(self, request, *args, **kwargs):

		data = request.POST
		print(data)
		form = ContactAboutTermsForm(data or None)
		if form.is_valid():
			if data['id'] == 'None':

				ContactAboutTerms.objects.create(about_us=form.cleaned_data['about_us'],
												 terms=form.cleaned_data['terms'],
												 contact_us=form.cleaned_data['contact_us'])
				messages.success(request, 'Created successfully')

			else:
				obj = ContactAboutTerms.objects.get(id=int(data['id']))
				obj.about_us = form.cleaned_data['about_us']
				obj.terms = form.cleaned_data['terms']
				obj.contact_us = form.cleaned_data['contact_us']
				obj.save()
				messages.success(request, 'Updated successfully')

			return HttpResponseRedirect('/admin/panel/terms_about_contact/')

		context = {
			'form': form,
			'about_us': data['about_us'],
			'terms': data['terms'],
			'contact_us': data['contact_us'],
			'id': data.get('id'),

		}

		return render(request, 'admin_panel/settings_management/terms_about_contact.html', context)


class FAQView(View):

	def get(self, request, *args, **kwargs):
		faq_qs = Faq.objects.all()
		context = {
			'faqs': faq_qs
		}
		return render(request, 'admin_panel/settings_management/faq.html', context)

	def post(self, request, *args, **kwargs):
		data = request.POST
		form = FaqForm(request.POST or None)
		if form.is_valid():
			if data['id'] == 'None' or data['id'] == '':

				Faq.objects.create(query=form.cleaned_data['query'],
								   answer=form.cleaned_data['answer'])
				messages.success(request, 'Created successfully')

			else:
				obj = Faq.objects.get(id=int(data['id']))
				obj.query = form.cleaned_data['query']
				obj.answer = form.cleaned_data['answer']
				obj.save()
				messages.success(request, 'Updated successfully')

			return HttpResponseRedirect('/admin/panel/faq/')

		context = {
			'form': form,
			'about_us': data['query'],
			'terms': data['answer'],
			'id': data.get('id'),

		}

		return render(request, 'admin_panel/settings_management/faq.html', context)

