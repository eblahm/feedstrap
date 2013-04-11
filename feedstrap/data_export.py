from django.http import HttpResponse
from models import Resource
import render

def weekly_reads_format(request):
    results = Resource.objects.all()
    v = {'results':results}
    response = HttpResponse(content_type='application/msword')
    response['Content-Disposition'] = 'attachment; filename="Weekly Read Export.html"'
    template_file = '/templates/main/wr_email.html'
    ms_doc = render.load(template_file, v)
    response.write(ms_doc)
    return response