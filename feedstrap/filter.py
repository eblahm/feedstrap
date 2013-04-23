import config
from models import generate_choices
from django.shortcuts import render
from django.http import HttpResponse
import models
from django import forms
from django.core.context_processors import csrf
from datetime import datetime


class FilterForm(forms.Form):
    search_term = forms.CharField(max_length=100)
    tags = forms.CharField(max_length=100)
    date_from = forms.DateField('%Y-%m-%d')
    date_to = forms.DateField('%Y-%m-%d')
    esil = forms.MultipleChoiceField(choices=generate_choices(models.Topic))
    office = forms.MultipleChoiceField(choices=generate_choices(models.Office))
    individual = forms.MultipleChoiceField(choices=generate_choices(models.Feed, 'owner'))
    report = forms.MultipleChoiceField(choices=generate_choices(models.Report))


def main(request):
    if request.method == "GET":
        perams = request.GET.dict()
        v = {}
        if len(perams) == 0:
            template_file = config.app_root + '/feedstrap/templates/main/forms/filter.html'
            form = FilterForm()
            return render(request, template_file, {'form': form, 'foo':'foo'})
        else:
            foo = True
            return HttpResponse('fail')
