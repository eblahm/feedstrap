from datetime import datetime
import pytz
import urllib

from django.contrib.auth.models import Permission
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm, UserCreationForm
from django.core import mail

from models import Invitee, Office, PostIt
from edit import create_new_postit
import render


class Profile(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    office = forms.CharField(max_length=100)
    email = forms.EmailField()

def info(request):
    if request.user.is_authenticated():
        v = {}
        v['nav'] = "info"
        v['host_url'] = request.get_host()
        if str(v['host_url'])[:3] != 'htt':
            v['host_url'] = 'http://' + v['host_url']

        if not PostIt.objects.filter(user=request.user): create_new_postit(request.user)
        usr_xtd = PostIt.objects.get(user=request.user)
        v['user_xtd_office'] = usr_xtd.office

        template_file = "main/user/info.html"
        return render.response(request, template_file, v)
    else:
        return HttpResponseRedirect('/signin?redirect=%s' % (urllib.quote(request.get_full_path())))

def main(request):
    errors = False
    if request.user.is_authenticated():

        usr = request.user
        usr_xtd = PostIt.objects.filter(user=usr)
        if not usr_xtd:
            usr_xtd = create_new_postit(usr)
        else:
            usr_xtd = usr_xtd.get()

        v = {}
        if request.method == "POST":
            user_input = request.POST.copy()
            f = Profile(user_input)
            if f.is_valid():
                usr = User.objects.get(pk=usr.pk)
                usr.email = user_input['email']
                usr.first_name = user_input['first_name']
                usr.last_name = user_input['last_name']
                usr.save()

                office, created = Office.objects.get_or_create(name=user_input['office'])
                usr_xtd.office = office
                usr_xtd.save()

                v['saved'] = True
                v['datetime'] = datetime.now().replace(tzinfo=pytz.timezone('America/New_York')).strftime('%I:%M:%S%p').lower() + " EST"
            else:
                errors = True

        if errors == True:
            v['Profile'] = f

        else:
            input = {'email': usr.email, 'first_name': usr.first_name, 'last_name': usr.last_name}
            if usr_xtd.office:
                input['office'] = usr_xtd.office.name
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
        username = request.POST['username'].lower()
        password = request.POST['password']
        user = authenticate(username=username, password=password) or \
        authenticate(username=username.title(), password=password)
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



def signup(request, secret):
    q = Invitee.objects.filter(has_accepted = False).filter(url_secret=secret)
    if q:
        invitee = q.get()
    else:
        return render.not_found(request)

    if request.method == "GET":
        return render.response(request,
                               'main/user/signup.html',
                               {'invitee': invitee,
                                'secret': secret})

    if request.method == "POST":
        inputs = request.POST.copy()
        inputs['email'] = invitee.email
        inputs['username'] = inputs['username'].lower()
        f = UserCreationForm(inputs)
        if f.is_valid():
            f.save()
            user = User.objects.get(username=f.cleaned_data['username'])
            user.email = invitee.email
            if inputs.get('first_name', ''):
                user.first_name = inputs['first_name']
            if inputs.get('last_name', ''):
                user.last_name = inputs['last_name']
            esil_view_all = Permission.objects.get(codename='view_all')
            user.save()
            postit = create_new_postit(user)
            if inputs.get('office', '').strip():
                office, created = Office.objects.get_or_create(name=inputs['office'])
                postit.office = office
                postit.feed.offices.add(office)
                postit.save()

            password = f.cleaned_data['password1']
            user = authenticate(username=user.username, password=password)
            login(request, user)
            invitee.has_accepted = True
            invitee.save()
            return HttpResponseRedirect("/esil")
        else:
            return render.response(request,
                                   'main/user/signup.html',
                                   {'invitee': invitee,
                                    'form': f,
                                    'secret': secret})

def parse(request):
    if request.method == "POST" and request.user.is_superuser:
        import re

        emails = request.POST['emails'].encode('utf8').strip()
        if emails:
            emails = [e.strip() for e in emails.split(';')]
            exists = \
            [str(u.email).lower() for u in User.objects.all()] + \
            [str(i.email).lower() for i in Invitee.objects.all()]

            parsed = []
            malformed = []
            already_exists = []

            def add_if_non_existant(canidate_email):
                if str(canidate_email).lower() in exists:
                    already_exists.append(canidate_email)
                else:
                    parsed.append(canidate_email)

            for e in emails:
                e = e.strip()
                # test 1 > is this email already in the system?
                if str(e).lower() in exists:
                    continue

                # test 2 > is the email formated like: Joe <joe@gmail.com>
                found = re.search('\<(.*?@.*?)\>', e)
                if found:
                    add_if_non_existant(found.group(1).strip())
                    continue

                # test 3 > is the email formated like: Joe (joe@gmail.com)
                # or in rare case: Joe (company) (joe@gmail.com)
                found = re.search('\((.*?@.*?)\)', e)
                if found:
                    p = found.group(1).strip()

                    if '(' in p:
                        p = p.split('(')[-1]
                    add_if_non_existant(p)

                    continue

                # test 4 > is the email formated like: joe@gmail.com
                found = re.search('^(.*?@.*?)$', e)
                if found:
                    add_if_non_existant(found.group(1).strip())
                    continue

                # reject > malformed email
                malformed.append(e)

            return render.response(request, 'admin/invitee/confirm.html', {
                'parsed': parsed,
                'malformed': malformed,
                'already_exists': already_exists
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
        messages = []
        for e in emails:
            new = Invitee(email = e)
            new = new.save()
            messages.append(new.invite(connection=email_connection))

        email_connection.send_messages(messages)
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
