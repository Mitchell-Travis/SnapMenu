from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from PIL import Image
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os



# Custom User Model

class UserManager(BaseUserManager):
	# Registering with email, username, and password
	def create_user(self, email, username, password=None):
		if not email:
			raise ValueError("User must have an email address")
		if not username:
			raise ValueError("User must have a username")
		user = self.model(
			email=self.normalize_email(email),
			username=username
		)
		user.set_password(password)
		user.save(using=self._db)
		return user

	# Creating the superuser
	def create_superuser(self, email, username, password):
		user = self.create_user(
			email=self.normalize_email(email),
			username=username,
			password=password
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user


# The filepath to the profile image
def get_profile_image_filepath(self, filename):
	return 'profile_images/' + str(self.pk) + '/profile_image.jpg'


# for default profile image
def get_default_profile_image():
	return "default.jpg"


# User model
class User(AbstractBaseUser, PermissionsMixin):
	email 					= models.EmailField(verbose_name='email', max_length=30, unique=True)
	username				= models.CharField(max_length=30, verbose_name='username', unique=False)
	first_name				= models.CharField(max_length=30, verbose_name='first name', null=True, blank=True)
	last_name				= models.CharField(max_length=30, verbose_name='last name', null=True, blank=True)
	last_login				= models.DateTimeField(verbose_name='last login', auto_now_add=True)
	date_joined				= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	is_admin 				= models.BooleanField(default=False)
	is_staff 				= models.BooleanField(default=False)
	is_active 				= models.BooleanField(default=True)
	is_superuser 			= models.BooleanField(default=False)
	hide_email				= models.BooleanField(default=True)
	profile_image			= models.ImageField(max_length=230, upload_to=get_profile_image_filepath, default=get_default_profile_image, blank=True, null=True)

	
	USERNAME_FIELD = 'email' # this is for you sign-in with your email
	REQUIRED_FIELDS = ['username'] # This username field is required by 
								   # django to create a custon user model

	objects = UserManager()

	def __str__(self):
		return self.username

	def get_profile_image_filename(self):
		return str(self.profile_image)[str(self.profile_image).index('profile_images/' + str(self.pk) + "/"):]

	# For checking permissions. to keep it simple all admin have ALL permissons
	def has_perm(self, perm, obj=None):
		return self.is_admin

	# Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
	def has_module_perms(self, app_label):
		return True


# Model for sending email confirmation code
class ConfirmationCode(models.Model):
	user 					= models.OneToOneField(User, on_delete=models.CASCADE, db_constraint=False, blank=True, null=True)
	confirmed_code				= models.CharField(max_length=30)

	def __str__(self):
		return self.confirmed_code


# Model for verifying the confirmation code
class VerifyConfirmation(models.Model):
	user 					= models.OneToOneField(User, on_delete=models.CASCADE, db_constraint=False, blank=True, null=True)
	verified_code 			= models.CharField(max_length=30)


	def __str__(self):
		return self.verified_code