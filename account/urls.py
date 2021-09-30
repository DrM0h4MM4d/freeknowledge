from django.urls import path
from django.urls.base import reverse_lazy
from . import views
from django.contrib.auth import views as _

app_name = 'account'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', views.ActivateUserEmailView.as_view(), name='activate'),
    path('active/again', views.SendEmailConfirmationLinkAgain.as_view(), name="active-again"),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('update/<int:pk>/', views.UpdateUserProfileView.as_view(), name='update'),
    path('delete/', views.ajax_delete_user, name='delete'),
    path('users/', views.AdministratorUsersManagerView.as_view(), name='users'),
    path('user/contacts/', views.ContactsView.as_view(), name='contacts'),
    path('dashboard/search/', views.DashboardSearchView.as_view(), name='dashboard-search'),
    path('administrator/website/system/chart/', views.ChartSystem.as_view(), name='chart'),
    path('ajax/validator/username', views.validate_username, name='validator-username'),
    path('ajax/validator/email', views.validate_email, name='validator-email'),
    path('ajax/validators/slug', views.ajax_slug_validators, name='aj-sl-val'),
    path('ajax/notification/read', views.notification_read_ajax, name='notif-read'),
    path('ajax/passwords/match', views.login_password_matches, name='validator-ps'),
    path('ajax/author/req', views.ajax_author_req, name='author-req'),
    path('contact/create/', views.CreateContactView.as_view(), name='contact-create'),
    path('contact/update/<int:pk>/', views.UpdateContactView.as_view(), name='contact-update'),
    path('contact/delete/', views.ajax_delete_user_contact, name='contact-delete'),
    path('article/create/', views.CreateArticleView.as_view(), name='article-create'),
    path('article/update/<int:pk>/', views.UpdateArticleView.as_view(), name='article-update'),
    path('article/delete/', views.ajax_delete_article, name='article-delete'),
    path('article/preview/<int:pk>/', views.DetailArticlePreView.as_view(), name='article-preview'),
    path('articles/', views.ListArticleView.as_view(), name='articles'),
    path('article/wrote/<int:pk>/', views.article_wrote, name='article-wrote'),
    path('category/create/', views.CategoryCreate.as_view(), name='category-create'),
    path('categories/', views.CategoryAdminManagement.as_view(), name='categories'),
    path('category/update/<int:pk>/', views.CategoryUpdate.as_view(), name='category-update'),
    path('category/delete/', views.ajax_delete_category, name='category-delete'),
    path('notif/create/', views.NotificationCreator.as_view(), name='notif-create'),
    path('notifs/manage/', views.AllNotifications.as_view(), name='notifs-admin'),
    path('notif/delete/', views.ajax_delete_notifs, name="notif-delete"),
    path('message/create/', views.CreateMessage.as_view(), name="message-create"),
    path('messages/', views.MyMessages.as_view(), name='messages'),
    path('message/delete/', views.ajax_delete_messages, name='message-delete'),
    path('message/detail/<int:pk>/', views.MessageDetail.as_view(), name='message-detail'),
    path('message/update/<int:pk>/', views.MessageUpdate.as_view(), name="message-update"),
    path('comments/manage/', views.CommentManagement.as_view(), name='comments'),
    path('comments/publish/<int:pk>/', views.CommentPublisher.as_view(), name="comment-update"),
    path('comments/delete/', views.ajax_delete_comment, name='comment-delete'),
    path('user/creation/', views.AdminUserCreation.as_view(), name='user-create'),
    path('challenge/create/', views.CreateChallengeView.as_view(), name='challenge-create'),
    path('challenge/update/<int:pk>/', views.UpdateChallengeView.as_view(), name='challenge-update'),
    path('challenge/delete/', views.ajax_delete_challenges, name='challenge-delete'),
    path('challenges/', views.ChallengesView.as_view(), name='challenges'),
    path('views/', views.ViewsDetailPage.as_view(), name='views'),
    path('views/delete/', views.ajax_delete_view, name='view-delete'),
    path('views/likes/', views.LikedArticles.as_view(), name="article-likes"),
    path('article/like/delete/', views.ajax_delete_like, name='article-like-delete'),
] 

urlpatterns += [
    path('password_change/', _.PasswordChangeView.as_view(
        template_name='auth/registration/password_change.html',
        success_url=reverse_lazy('account:password_change_done')),
        name='password_change'),

    path('password_change/done/', _.PasswordChangeDoneView.as_view(
        template_name='auth/registration/password_change_done.html'),
        name='password_change_done'),

    path('password_reset/', _.PasswordResetView.as_view(
        template_name='auth/registration/password_reset.html',
        success_url=reverse_lazy('account:password_reset_done')),
        name='password_reset'),

    path('password_reset/done/', _.PasswordResetDoneView.as_view(
        template_name='auth/registration/password_reset_done.html'),
        name='password_reset_done'),

    path('reset/<uidb64>/<token>/', _.PasswordResetConfirmView.as_view(
        template_name='auth/registration/password_reset_confirm.html',
        success_url=reverse_lazy('account:password_reset_complete')),
        name='password_reset_confirm'),

    path('reset/done/', _.PasswordResetCompleteView.as_view(
        template_name='auth/registration/password_reset_complete.html'),
        name='password_reset_complete'),
]
