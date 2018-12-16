
# Create your views here.
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import get_object_or_404,render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import boto3
import urllib
import requests
from sqlalchemy import create_engine
from pandas.io import sql
import pandas as pd
import datetime
from  subprocess import call
import os
from .models import *

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

"""
def run_converter(request):
	try:
		my_env = {**os.environ, 'PATH':'/usr/local/USD/bin'+os.environ['PATH']}
		my_env['PYTHONPATH']="{}:{}".format(os.environ['PATH'],'/usr/local/USD/lib/python')
		call('/home/ubuntu/EyeKandy/sketch.sh', env=my_env, shell=True)
		r="Order received! Please check the output bucket in ten seconds!"
	except:
		r="Failure!"
	return  HttpResponse(r)
"""

def crawlLog(request, urle):
    qr=None
    s3 = boto3.resource('s3')
    bucket_name = 'diffbot-crawl'
    your_bucket = s3.Bucket(bucket_name)
    files=[]

    try:
        urle2=urle.replace("diffbot","%").replace("%C2%AC",".")
        urle2=urllib.parse.unquote(urle2)
        for s3_file in your_bucket.objects.all():
            files.append(s3_file.key)
        if (urle+"-"+str(int(round(time.time()/604800)))+".html") not in files:
            with open("details.txt","a+") as detail:
                detail.write(urle2+"\t"+str(time.time())+"\t"+"0\r\n")
                qr="logged!"
            with open("details.txt","r") as detail:
                s3=boto3.client('s3')
                filename = "details.txt"
                s3.upload_file(filename, bucket_name, filename,ExtraArgs={'ACL':'public-read'})
        else:
            reque=requests.get("https://s3-us-west-1.amazonaws.com/diffbot-crawl/"+urle+str(int(round(time.time()/604800)))+"-"+".html")
            qr=reque.text
    
    except:
        qr="something is broken!!"
        raise Http404("something is broken!!")
    
    finally:
        if not qr: qr="done"
        return HttpResponse(qr)
    

def postgres_url_logger(url='url'):
    err="error! check log!"
    try:
        db = create_engine("postgresql+psycopg2://postgres:uCL1+1=2@54.191.29.218:5432/qa_db",echo=False)
        df = pd.read_sql_query('select * from crawl_log',con=db,index_col='urli').reset_index()
        column_content=[url,str(datetime.datetime.utcnow()),None,None,None,None]
        df_new=pd.DataFrame.from_dict(dict(zip(df.columns,[[each]for each in column_content])))
        df_new.set_index('urli').to_sql(con=db, name='crawl_log',if_exists='append')
        err="URL logged!"
    except Exception as e:
        err=str(e)
    finally:
        if "duplicate key" in err:
            err="duplicate key!"
        return err
    
def crawl(request):
    qr=None
    s3 = boto3.resource('s3')
    bucket_name = 'diffbot-crawl'
    your_bucket = s3.Bucket(bucket_name)
    files=[]#filenames in the s3 bucket
    urle = request.GET.get('urle')
    urle2=urllib.parse.unquote(urle)
    file_format=urllib.parse.quote(urle,safe="").replace(".","dot")
    reque=requests.get("https://s3-us-west-1.amazonaws.com/diffbot-crawl/"+file_format+".html")
    #qr=postgres_url_logger(url=urle2)
    try:
        if not reque.ok:
            qr=postgres_url_logger(url=urle2)
        else:
            qr=reque.text
    
    except:
        qr="something is broken!!"
    
    finally:
        if not qr: qr="done!"
        return HttpResponse(qr)
    

def crawlFirefox2(request):
    try:
        urle = request.GET.get('urle')
        urle=urllib.parse.unquote(urle)
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(firefox_options=options)
        qt=("Firefox Headless Browser Invoked")
        print(qt)
        driver.get(urle)
        time.sleep(15)
        qr=driver.page_source
        driver.quit()
        if not qr:
            raise Http404("crawler did not run!!")
    
    except:
        raise Http404("something is broken!!")
    
    finally:
        if not qr: 
            qr="Nothing was found!! Error"
            if (qt): qr=qr+" "+qt
        return HttpResponse(qr)
    
def crawlFirefox(request, urle):
    try:
        urle=urle.replace("diffbot","%")
        urle=urle.replace("%C2%AC",".")
        urle=urllib.parse.unquote(urle)
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(firefox_options=options)
        qt=("Firefox Headless Browser Invoked")
        driver.get(urle)
        time.sleep(15)
        qr=driver.page_source
        driver.quit()
        if not qr:
            raise Http404("crawler did not run!!")
    
    except:
        raise Http404("something is broken!!")
    
    finally:
        if not qr: 
            qr="Nothing was found!! Error"
            if (qt): qr=qr+" "+qt
        return HttpResponse(qr)

def vote(request, question_id):
    question=get_object_or_404(Question,pk=question_id)
    try:
       selected_choice=question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
       #Redisplay the question voting form.
       return render(request, 'polls/detail.html', {
           'question':question,
           'error_message': "You didn't select a choice.",
            })
    else:
        selected_choice.votes +=1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

"""
Removed code!
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    question=get_object_or_404(Question,pk=question_id)
    return render(request, 'polls/results.html',{'question':question})
"""
