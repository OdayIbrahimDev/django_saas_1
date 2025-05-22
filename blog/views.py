from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from .models import Profile, Tag, Article
from tenant.models import Tenant

# Django Q objects use to create complex queries
# https://docs.djangoproject.com/en/3.2/topics/db/queries/#complex-lookups-with-q-objects
from django.db.models import Q


def home(request):

    # feature articles on the home page
    featured = Article.articlemanager.filter(featured=True)[0:3]
    # get the blog name from the tenant model
    # and set it to the title of the page
    dominTitle = request.get_host().split('.')[0]
    try:
        titleName = Tenant.objects.get(blog_name=dominTitle)
        titleName = titleName.blog_name
    except Tenant.DoesNotExist:
        titleName = 'Blogx'
    #blogName = Tenant.objects.values_list('blog_name',flat=True)
    # for title in blogName:
    #     if title != dominTitle:
    #         titleName = 'Blogx'  
    #     else:
    #         titleName = title  
    context = {
        'articles': featured,
        'title'   : titleName
    }
    return render(request, 'index.html', context)


def articles(request):

    # get query from request
    query = request.GET.get('query')
    # print(query)
    # Set query to '' if None
    if query == None:
        query = ''

    # articles = Article.articlemanager.all()
    # search for query in headline, sub headline, body
    articles = Article.articlemanager.filter(
        Q(headline__icontains=query) |
        Q(sub_headline__icontains=query) |
        Q(body__icontains=query)
    )

    tags = Tag.objects.all()

    context = {
        'articles': articles,
        'tags': tags,
    }

    return render(request, 'articles.html', context)


def article(request, article):

    article = get_object_or_404(Article, slug=article, status='published')

    context = {
        'article': article
    }

    return render(request, 'article.html', context)
