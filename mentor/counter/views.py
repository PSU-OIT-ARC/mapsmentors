import csv
from django.shortcuts import render
from mentor.counter.models import Counter 
from datetime import date, datetime, timedelta 
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.timezone import localtime

from django.contrib.admin.views.decorators import staff_member_required
from mentor.questionaire.forms import DownloadResponseForm
from django.db.models import Count
import pytz 
from django.conf import settings
# Create your views here.

def goto(request, url=None):
    url = request.GET.get('url',None)   
    # import pdb; pdb.set_trace();
    if url:
        counter = Counter(url=url)
        counter.save()
        return HttpResponseRedirect(url)
    else:
        raise Http404()

@staff_member_required
def report(request):
    """
    This report view is to report a csv file contains all the counter data
    Only can viewed by staff members
    """
    title = " Click-through Data "
    if request.POST:
        form = DownloadResponseForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date'] + timedelta(days=1)

            our_timezone = pytz.timezone(settings.TIME_ZONE)
            start_date_tz = our_timezone.localize(datetime.combine(start_date, datetime.min.time()))
            end_date_tz = our_timezone.localize(datetime.combine(end_date, datetime.min.time()))

            counters = Counter.objects.filter(timestamp__lt=end_date_tz,timestamp__gte=start_date_tz)
            filename = "Report Click-through data from " + start_date.strftime("%Y-%m-%d") + " to " + end_date.strftime("%Y-%m-%d")

            http_response = HttpResponse()
            http_response = HttpResponse(content_type='text/csv')
            http_response['Content-Disposition'] = 'attachment; filename="%s.csv"' % (filename)

            
            writer = csv.writter(http_response)
            header = ["url", "timestamp"]
            writer.writerow(header)
            
            for counter in counters:
                csv_row = []
                csv_row.append(counter.url)
                csv_row.append(localtime(counter.timestamp).strftime("%Y-%m-%d %H:%M:%S"))
    
                writer.writerow(csv_row)

            return http_response
    else:
        form = DownloadResponseForm()

    return render(request, "admin/download_csv.html", {
        "form" : form,
        "title" : title,
    })

@staff_member_required
def list_counter(request):
    counters = []
    if request.POST:
        form = DownloadResponseForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date'] + timedelta(days=1)

            counters = Counter.objects.raw('''
                SELECT *, COUNT(url) AS url_count FROM counter 
                WHERE timestamp >= "''' + start_date.strftime("%Y-%m-%d %H:%M:%S") + '''" and timestamp < "''' + end_date.strftime("%Y-%m-%d %H:%M:%S") + '''"
                GROUP BY url;''')
    else:
        form = DownloadResponseForm()
        counters = Counter.objects.raw('''
                SELECT *, COUNT(url) AS url_count FROM counter 
                GROUP BY url;''')

    return render(request, "admin/counter_list.html", {
        "counters" : counters,
        "form" : form,
        "has_counters" : len(list(counters)),
    })
