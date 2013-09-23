from datetime import datetime
import pytz
import urllib

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.core import mail

from models import Feed, Invitee
from admin import InviteeAdmin
import render


class Profile(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

def info(request):
    v = {}
    v['nav'] = "info"
    v['host_url'] = request.get_host()
    if str(v['host_url'])[:3] != 'htt':
        v['host_url'] = 'http://' + v['host_url']
    template_file = "main/user/info.html"
    return render.response(request, template_file, v)


def main(request):
    errors = False
    if request.user.is_authenticated():
        usr = request.user
        v = {}
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
            else:
                errors = True
        if errors == True:
            v['Profile'] = f
        else:
            input = {'email': usr.email, 'first_name': usr.first_name, 'last_name': usr.last_name, 'feeds': ['foo']}
            v['Profile'] = Profile(initial=input)

        v.update(csrf(request))
        v['nav'] = "profile"
        template_file = "main/user/edit.html"
        return render.response(request, template_file, v)

def psw(request):
    errors = False
    v = {}
    if request.user.is_authenticated():
        if request.method == "POST":
            f = SetPasswordForm(request.user, request.POST.dict())
            if f.is_valid():
                f.save()
                v['pchanged'] = True
                v['datetime'] = datetime.now().replace(tzinfo=pytz.timezone('America/New_York')).strftime('%I:%M:%S%p').lower() + " EST"

                usr = User.objects.get(pk=request.user.pk)
                input = {'email': usr.email, 'first_name': usr.first_name, 'last_name': usr.last_name, 'feeds': ['foo']}
                v['Profile'] = Profile(initial=input)
                v.update(csrf(request))
                v['nav'] = "profile"
                template_file = "main/user/edit.html"

                return render.response(request, template_file, v)
            else:
                errors = True
        if request.method == "GET" or errors == True:
            if errors == True:
                v['f'] = PasswordChangeForm(request.user, request.POST.dict())
            else:
                v['f'] = PasswordChangeForm(request.user)
            v.update(csrf(request))
            v['nav'] = "profile"
            template_file = "main/user/psw_change.html"
            return render.response(request, template_file, v)



def signin(request):
    v = {'invalid': False}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if request.POST['redirect'] != "":
                    return HttpResponseRedirect(urllib.unquote(request.POST['redirect']))
                else:
                    return HttpResponseRedirect('/')
            else:
                return render.not_found(request)
        else:
            v['invalid'] = True
    if request.method == 'GET' or v['invalid'] == True:
        v['redirect'] = request.REQUEST.get('redirect', "")
        v.update(csrf(request))
        template_file = "main/forms/signin.html"
        return render.response(request, template_file, v)

def signout(request):
    logout(request)
    return HttpResponseRedirect('/')


def parse(request):
    if request.method == "POST" and request.user.is_superuser:
        import re
        
        emails = request.POST['emails'].encode('utf8').strip()
        if emails:
            emails = [e.strip() for e in emails.split(';')]
            parsed = []
            malformed = []
            for e in emails:
                
                found = re.search('\<(.*?@.*?)\>', e)
                if found:
                    parsed.append(found.group(1).strip())
                    continue
                
                found = re.search('\((.*?@.*?)\)', e)
                if found:
                    p = found.group(1).strip()
                    if '(' in p:
                        p = p.split('(')[-1]
                    parsed.append(p)
                    
                    continue
                
                found = re.search('^(.*?@.*?)$', e)
                if found:
                    parsed.append(found.group(1).strip())
                    continue
                
                if '@' in e:
                    parsed.append(e)
                else:
                    malformed.append(e)
                    
            return render.response(request, 'admin/invitee/confirm.html', {
                'parsed': parsed,
                'malformed': malformed
                })
        else:
            return render.not_found(request)
    else:
        return render.not_found(request)
    
        
def confirmed_invite(request):
    if request.method == "POST" and request.user.is_superuser:
        email_connection = mail.get_connection()
        email_connection.open()
        
        emails = request.POST.getlist('email')
        for e in emails:
            new = Invitee(email = e)
            new = new.save()
            new.invite(connection=email_connection)
        email_connection.close()
        
        return HttpResponseRedirect('/admin/feedstrap/invitee/')
    else:
        return render.not_found(request)
    
    
def invite(request, action):
    
    _run_action = {
        'parse': parse,
        'add': confirmed_invite
    }
    return _run_action.get(action, render.not_found)(request)