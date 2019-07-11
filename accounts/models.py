from django.db import models
from django.contrib.auth.models import AbstractUser

PRIVACY_TYPE = (('1', 'only me'), ('2', 'viewing'), ('3', 'public'))


class Languages(models.Model):
    lang_name = models.CharField(max_length=100)

    def __str__(self):
        return self.lang_name


class User(AbstractUser):

    """
    extend User model
    """

    PROFILE_TYPE = (('1', 'Personal'), ('2', 'Company'))
    GENDER = (('1', 'male'), ('2', 'female'))
    ACCOUNT_TYPE = (('1', 'normal'), ('2', 'fb'), ('3', 'instagram'), ('4', 'snapchat'), ('5', 'twitter'), ('6','google'))
    DEVICE_TYPE = (('1', 'android'), ('2', 'ios'))

    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    country_code = models.CharField(max_length=10, blank=True, null=True)
    profile_type = models.CharField(max_length=20, blank=True, choices=PROFILE_TYPE)
    is_mail_verify = models.BooleanField(default=False)
    is_num_verify = models.BooleanField(default=False)
    gender = models.CharField(max_length=20, choices=GENDER)
    birth_date = models.DateField(null=True, blank=True)
    birth_date_privacy = models.CharField(max_length=5, blank=True, choices=PRIVACY_TYPE)
    language = models.ManyToManyField(Languages, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(blank=True, upload_to='profile_image')
    cover_image = models.ImageField(blank=True, upload_to='cover_image')
    device_token = models.CharField(max_length=500, blank=True)
    device_type = models.CharField(max_length=5, blank=True, choices=DEVICE_TYPE)
    profile_views_count = models.PositiveIntegerField(default=0)

    # social login

    account_type = models.CharField(max_length=500, default=1, choices=ACCOUNT_TYPE)
    social_id = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.first_name + '-' + str(self.id)

    class Meta:
        unique_together = ('account_type', 'social_id')


class ViewingAndViewers(models.Model):
    """
    List of followers and following and their status
    """

    STATUS = (('1', 'pending'), ('2', 'accepted'), ('3', 'cancelled'))

    viewed_by = models.ForeignKey(User, on_delete=models.CASCADE,  related_name='viewed_by')
    viewed_to = models.ForeignKey(User, on_delete=models.CASCADE,  related_name='viewed_to')
    status = models.CharField(max_length=50, choices=STATUS)
    accepted_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.viewed_by.first_name + '-' + str(self.viewed_to.first_name)


class SocialLink(models.Model):

    """
    social links of user
    """
    SOCIAL_LINKS = (('1', 'facebook'), ('2', 'google'), ('3', 'twitter'), ('4', 'instagram'), ('5', 'linkedin'))

    social_link_type = models.CharField(max_length=5, blank=True, choices=SOCIAL_LINKS)
    link = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return str(self.id)


class Ethnicity(models.Model):
    country_name = models.CharField(max_length=100)
    flag = models.ImageField(upload_to='ethnicity_flag', blank=True)

    def __str__(self):
        return self. country_name


class UserContactInfo(models.Model):

    """
    Contact information of user
    """

    user_id = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contact_info')
    current_city = models.CharField(max_length=100, blank=True,)
    current_city_privacy = models.CharField(max_length=5, blank=True, choices=PRIVACY_TYPE)
    current_city_lat = models.CharField(max_length=100, blank=True)
    current_city_long = models.CharField(max_length=100, blank=True)
    hometown = models.CharField(max_length=100, blank=True,)
    hometown_privacy = models.CharField(max_length=5, blank=True, choices=PRIVACY_TYPE)
    hometown_lat = models.CharField(max_length=100, blank=True)
    hometown_long = models.CharField(max_length=100, blank=True)
    ethnicity = models.ManyToManyField(Ethnicity, blank=True)
    alt_mobile_number = models.CharField(max_length = 20, blank=True)
    country_code = models.CharField(max_length=10, blank=True)
    website_link = models.CharField(max_length=100, blank=True)
    social_link = models.ManyToManyField(SocialLink, blank=True)

    def __str__(self):
        return str(self.user_id) + '-' + str(self.id)


class UserInterests(models.Model):

    """
    interest of user
    """

    INTEREST_TYPE = (('1', 'activities'), ('2', 'hobbies'), ('3', 'music'), ('4', 'movies'), ('5', 'tv_shows'), ('6', 'games'))

    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_interest')
    interest_type = models.CharField(max_length=5, choices=INTEREST_TYPE)
    interest = models.CharField(max_length=100)

    def __str__(self):
        return str(self.user_id) + '-' + str(self.id)


class UserInterest(models.Model):
    """
    User interest
    """
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_interests')
    interest_text = models.TextField(blank=True)
    activities = models.CharField(max_length=500, blank=True)
    hobbies = models.CharField(max_length=500, blank=True)
    music = models.CharField(max_length=500, blank=True)
    movies = models.CharField(max_length=500, blank=True)
    tv_shows = models.CharField(max_length=500, blank=True)
    games = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return str(self.user_id) + '-' + str(self.id)


class UserEducationalDetails(models.Model):

    """
    educational detail of user
    """

    user_id = models.OneToOneField(User, on_delete=models.CASCADE, related_name='education_detail')
    college_name = models.CharField(max_length=200, blank = True)
    college_since = models.DateField(blank=True,null=True)
    secondary_school = models.CharField(max_length=100, blank=True)
    sec_class_year = models.PositiveSmallIntegerField(blank=True, null=True)
    high_school = models.CharField(max_length=100, blank=True)
    high_class_year = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.user_id) + '-' + str(self.id)


class UserWorkExperience(models.Model):

    """
    work experience of user
    """

    user_id = models.OneToOneField(User, on_delete=models.CASCADE, related_name='work_experience')
    company_name = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    location_lat = models.CharField(max_length=50, blank=True)
    location_long = models.CharField(max_length=50, blank=True)
    work_des = models.TextField(blank=True)
    is_working_here = models.BooleanField(default=False)
    working_since = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.user_id) + '-' + str(self.id)


class UserPersonalView(models.Model):

    """
    user view about different fields
    """

    user_id = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personal_view')
    political_view = models.TextField(blank=True)
    world_view = models.TextField(blank=True)
    religious_view = models.TextField(blank=True)

    def __str__(self):
        return str(self.user_id) + '-' + str(self.id)

