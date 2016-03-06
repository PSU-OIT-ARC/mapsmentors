from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

from django.contrib import admin
from mentor.questionaire import views as questionaire
from mentor.users import views as user

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', questionaire.add_questionaire, name='home'),

    # admin area
    url(r'^admin/', include(admin.site.urls), name='admin-home'),
    url(r'^admin/report-questionaire', questionaire.report, name='questionaire-reporting'),

    # mentor area
    url(r'^mentor/home', user.mentor_home, name="mentor-homepage"),
    url(r'^mentor/response/detail/(?P<response_id>\d+)/?$', user.response_detail, name="response-detail"),
    url(r'^mentor/response/resolve/(?P<response_id>\d+)/?$', user.response_resolve, name="response-resolve"),

    # Questionaire
    url(r'^questionaire/add/?$', questionaire.add_questionaire, name='questionaire-adding'),
    url(r'^questionaire/thanks/?$', TemplateView.as_view(template_name='questionaire/thanks.html'), name='questionaire-thanks'),
)

# CAS authentication
urlpatterns += patterns('',
    url(r'^accounts/login/$', 'arcutils.cas.views.login', name='account-login'),
    url(r'^accounts/logout/$', 'arcutils.cas.views.logout', name='account-logout'),
    url(r'^accounts/validate/$', 'arcutils.cas.views.validate', name='cas-validate'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
