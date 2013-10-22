import render
from models import Tag
from django.contrib.auth.decorators import user_passes_test


@user_passes_test(lambda u: u.is_superuser)
def TagsWidget(request):
 
    return render.response(request, template_file, v)
