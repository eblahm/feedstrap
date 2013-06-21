from django.http import HttpResponse, HttpResponseRedirect
from filter import apply_filter, generate_filter_tags
import render
from models import UserProfile, Feed
from django.core.context_processors import csrf
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
import pytz
from datetime import datetime


class upf(ModelForm):
    class Meta:
        model = UserProfile


class Profile(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

def main(request):
    if request.user.is_authenticated():
        usr = request.user
        v = {'user_obj': request.user}
        feed = Feed.objects.all()[0]
        v['feeds'] = [(feed.name, feed.url)]
        if request.method == "POST":
            user_input = request.POST.dict()
            pops = []
            for k in user_input:
                if k.split("_")[0] == "feed":
                    pops.append(k)
            for p in pops:
                user_input.pop(p)
            f = Profile(user_input)
            if f.is_valid():
                usr = User.objects.get(pk=usr.pk)
                usr.email = user_input['email']
                usr.first_name = user_input['first_name']
                usr.last_name = user_input['last_name']
                usr.save()
            v['saved'] = True
            v['datetime'] = datetime.now().replace(tzinfo=pytz.timezone('America/New_York')).strftime('%I:%M:%S%p').lower() + " EST"

        input = {'email': usr.email, 'first_name': usr.first_name, 'last_name': usr.last_name, 'feeds': ['foo']}
        v['Profile'] = Profile(initial=input)

        v.update(csrf(request))
        template_file = "/user/profile.html"
        return HttpResponse(render.load(template_file, v))
