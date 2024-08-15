from django.contrib import admin
from .models import InconvenienceRequest, InconvenienceRequestLine, Day
# Register your models here.

admin.site.register(InconvenienceRequest)
admin.site.register(InconvenienceRequestLine)
admin.site.register(Day)