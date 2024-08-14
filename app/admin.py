from django.contrib import admin
from app.models import Contact
from django.contrib.auth.models import User
from app.models import user_details
admin.site.register(Contact)
admin.site.register(user_details)
admin.site.register(User)