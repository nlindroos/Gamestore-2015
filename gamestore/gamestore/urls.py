from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gamestore.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # TODO: Uncomment social to enable google login
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('store.urls')),
    #url('', include('social.apps.django_app.urls', namespace='social')),
)