from blog.models import ViewsMid
from django.db.models import Q
from django.http import JsonResponse
from .forms import CommentCreationForm
from .models import Article, Category, Likes, Comment
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib.auth.decorators import login_required
from account.models import UserProfile


# Create your views here.
class HomePageView(generic.View): 
    def get(self, request):
        posts = Article.objects.filter(published='p').order_by('-slug')[:9]
        categories = Category.objects.all()

        context = {
            'posts': posts,
            'categories': categories,
            'titlex': 'صفحه اصلی',
        }

        return render(request, 'index.html', context)


class SearchPageView(generic.View):
    def get(self, request):
        posts = Article.objects.filter(published='p').order_by('-slug')[:5]
        categories = Category.objects.all()

        return render(request, 'search.html', {'posts': posts, 'categories': categories})

    def post(self, request):
        last_posts = Article.objects.filter(published='p').order_by('-slug')[:5]
        categories = Category.objects.all()

        keyword = request.POST.get('title')
        result = Article.objects.filter(Q(title__icontains=keyword) |
                                        Q(text__icontains=keyword) |
                                        Q(slug__icontains=keyword) |
                                        Q(category__title__icontains=keyword) |
                                        Q(author__first_name__icontains=keyword) |
                                        Q(author__last_name__icontains=keyword) |
                                        Q(author__username__icontains=keyword))
        return render(request, 'search.html', {'articles': result,
                                               'posts': last_posts,
                                               'categories': categories,
                                               'title': 'نتیجه جستجو ' + f'"{keyword}"'
                                               })


class ArticleListView(generic.ListView): 
    paginate_by = 9
    queryset = Article.objects.filter(published='p')
    model = Article
    template_name = 'articles.html'
    context_object_name = 'articles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Article.objects.filter(published='p').order_by('-slug')[:9]
        categories = Category.objects.all()

        context['posts'] = posts
        context['categories'] = categories
        context['title'] = 'مقالات'
        return context


class ArticleDetailView(generic.View):
    def get(self, request, slug):
        comment_form = CommentCreationForm()
        article = get_object_or_404(Article, published='p', slug=slug)
        categories = Category.objects.all()[:5]
        latest_articles = Article.objects.filter(published='p')[:5]
        comments = Comment.objects.filter(to_article=article.pk, published=True)
        articles = Article.objects.all()[:5]
        try:
            user_ip = ViewsMid.objects.get(ip_addr=request.user.ip_address)
        except ViewsMid.DoesNotExist:
            user_ip = ViewsMid.objects.create(ip_addr=request.user.ip_address, ua=request.user.ua, user=request.user)
        
        view = article.hits.count()
        author = article.author

        context = {
            'form': comment_form,
            'article': article,
            'view': view,
            'comments': comments,
            'author': author,
            'categories': categories,
            'last_articles': latest_articles,
            'posts': articles,
            'title': article.title
        }
        return render(request, 'article.html', context)

    def post(self, request, slug):
        article = Article.objects.get(published='p', slug=slug)
        form = CommentCreationForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.from_user = request.user
            comment.to_article = article
            comment.published = False
            comment.save()

            return redirect('account:comments')


class CategoryRelatedToAnArticleView(generic.ListView): 
    model = Article
    context_object_name = 'articles'
    template_name = 'category.html'

    def get_queryset(self):
        return Article.objects.filter(category__slug=self.kwargs['slug'], published='p')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Article.objects.filter(published='p').order_by('-slug')[:9]
        categories = Category.objects.all()

        context['posts'] = posts
        context['categories'] = categories
        context['title'] = Category.objects.get(slug=self.kwargs['slug']).title
        return context


class ViewProfile(generic.DetailView):
    model = UserProfile
    context_object_name = 'author'
    slug_field = 'username'
    template_name = 'author.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Article.objects.filter(published='p').order_by('-slug')[:9]
        categories = Category.objects.all()

        context['posts'] = posts
        context['categories'] = categories
        context['title'] = 'مشاهده پروفایل'
        return context


class ViewAuthorProfiles(generic.ListView): 
    model = UserProfile
    context_object_name = 'authors'
    queryset = UserProfile.objects.filter(is_author=True)
    template_name = 'authors.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Article.objects.filter(published='p').order_by('-slug')[:9]
        categories = Category.objects.all()

        context['posts'] = posts
        context['categories'] = categories
        context['title'] = 'نویسندگان'
        return context
    

class Challenges(generic.View):
    def get(self, request):
        posts = Article.objects.filter(published='p').order_by('-slug')[:9]
        categories = Category.objects.all()
        context = {}
        context['posts'] = posts
        context['categories'] = categories
        context['title'] = 'چالش ها'
        return render(request, 'challenge.html', context)


class AboutUsPage(generic.View):
    def get(self, request):
        context = {
            'categories': Category.objects.all()[:5],
            'posts': Article.objects.all()[:5],
            'title': 'درباره'
        }
        return render(request, 'about.html', context)


class ContactUsPage(generic.View):
    def get(self, request):
        context = {
            'categories': Category.objects.all()[:5],
            'posts': Article.objects.all()[:5],
            'title': 'ارتباط'
        }
        return render(request, 'contact.html', context)


@login_required
def liker(request):
    if request.method == "POST" and request.is_ajax:
        pk = request.POST.get("id")
        post = Article.objects.get(pk=pk)
        try:
            like = Likes.objects.get(user=request.user, post=post)
            like.delete()
            return JsonResponse({
                'disliked': True
            })
        except Likes.DoesNotExist:
            Likes.objects.create(user=request.user, post=post)
            return JsonResponse({
                'liked': True
            })


def send_likes_count_ajax(request):
    if request.is_ajax and request.method == "POST":
        pk = request.POST.get("wal")
        try:
            article = Article.objects.get(pk=pk)
            return JsonResponse({
                "likes": article.likes.count()
            })
        except Article.DoesNotExist:
            return JsonResponse({
                "Error": 503
            })
