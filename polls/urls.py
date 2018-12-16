from django.urls import path
from . import views

app_name = 'polls'

urlpatterns = [
    # ex: /polls/
    path('', views.IndexView.as_view(), name='index'),
    # ex: /polls/5/
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # ex: /polls/5/results/
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # ex: /polls/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
    # ex: /polls/5/vote/
    path('<str:urle>/crawl/', views.crawlFirefox, name='crawlFirefox'),
    # ex: /polls/5/vote/
    path('crawl/', views.crawl, name='stdCrawl'),
    # ex: /polls/5/vote/
    path('icrawl/', views.crawlFirefox2, name='crawlFirefox2'),
    # ex: /polls/5/vote/
    path('<str:urle>/log/', views.crawlLog, name='crawlLog'),
    # ex: /polls/5/vote/
    #path('usdz/', views.run_converter, name='usdzconverter'),
]
