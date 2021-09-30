from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('authors/profiles/', views.ViewAuthorProfiles.as_view(), name='authors'),
    path('author/profile/<str:slug>/', views.ViewProfile.as_view(), name='author'),
    path('', views.HomePageView.as_view(), name='home'),
    path('posts/list/', views.ArticleListView.as_view(), name='posts'),
    path('post/detail/<str:slug>/', views.ArticleDetailView.as_view(), name='detail'),
    path('post/search/', views.SearchPageView.as_view(), name='search'),
    path('posts/category/<str:slug>/', views.CategoryRelatedToAnArticleView.as_view(), name='article-related-category'),
    path('about/', views.AboutUsPage.as_view(), name='about'),
    path('contact/', views.ContactUsPage.as_view(), name="contact"),
    path('ajax/like', views.liker, name="like"),
    path('ajax/like/update', views.send_likes_count_ajax, name="likeupdate"),
]
