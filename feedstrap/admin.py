from django.contrib import admin
from feedstrap.models import *

for data_model in allow_admin_for:
    admin.site.register(data_model)