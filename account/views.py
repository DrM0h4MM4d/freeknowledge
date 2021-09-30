from extensions.bot_send_to_channel import send_to_channel
from django.db.models import Q
from .utils import check_email_spam
import re
from django.db.models import Count
from django.template.loader import render_to_string
from django.contrib.auth.forms import UserCreationForm
from django.http.response import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import timedelta, datetime
from .tasks import send_email
from .models import (
    ChallengeEvent,
    ContactsUser,
    Message,
    NotificationAdminCenter,
    UserProfile
)
from django.contrib.auth import (
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
    authenticate
)
from .forms import (
    AgainEmailConfirmationForm,
    CreateArticleForm,
    CreateUserContactsForm,
    MessageForm,
    NotificationCreatorForm,
    UpdateUserArticleForm,
    UpdateUserAccountForm,
    UpdateUserContactsForm,
    UserLoginForm,
    UserRegistrationForm,
    UserSetPassword
)
from .mixins import (
    ArticleCreateFormMixin,
    ArticlePreviewMixin,
    ContactCreateFormMixin,
    IsArticleCreatorOr404Mixin,
    IsAuthorOrSuperUserOr404,
    IsContactCreatorOr404Mixin,
    IsSelfOr404Mixin,
    SuperUserMixinRequired
)
from blog.models import (
    Article,
    Comment,
    Category,
    ViewsMid,
    Likes,
)

User = get_user_model()


# Create your views here.
class UserLoginView(generic.View):

    def get(self, request):
        form = UserLoginForm()
        return render(request, 'auth/registration/login.html', {'form': form})
    
    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            if not remember_me:
                request.session.set_expiry(0)

            user = authenticate(username=username, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(message="عزیز {}, شما وارد اکانتتان شدید!", request=request)
                return redirect("account:dashboard")
            else:
                # return HttpResponse("User Does Not Exists")
                return render(request, 'auth/registration/login.html',
                              {'error': 'کاربری با این مشخصات وجود ندارد', 'form': form})
        else:
            return render(request, 'auth/registration/login.html', {'form': form})


class LogoutView(generic.View):

    def get(self, request):
        logout(request)
        messages.success(message="شما از اکانتتان خارج شدید!", request=request)
        return redirect('blog:home')


class UserRegistrationView(generic.View):

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username, email = form.cleaned_data.get("username"), form.cleaned_data.get("email")
            if UserProfile.objects.filter(Q(username=username) | Q(email=email)).exists():
                return HttpResponse("اکانتی با این مشخصات وجود دارد")
            else:
                user = UserProfile.objects.create(username=username, email=email, is_active=False)
            if check_email_spam(email):
                current_site = get_current_site(request)
                mail_subject = 'اکانت خود را تایید کنید.'
                message = render_to_string('auth/acc_active_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                    })
                to_email = email
                send_email.delay(mail_subject, message, to_email)
                return HttpResponse("ایمیل خود را تایید کنید")
            else:
                return HttpResponse("""ما قبلا به شما ایمیل ارسال کردیم،"
                                    برای جلوگیری از اسپم لطفا 3 دقیقه صبر کنید و. دوباره تلاش کنید.""")
        else:
            return HttpResponse("فرم اشتباه پر شده است")

    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'auth/register.html', {'form': form})


class SendEmailConfirmationLinkAgain(generic.View):
    def get(self, request):
        form = AgainEmailConfirmationForm()
        return render(request, 'auth/again_email_activation.html', {'form': form})
            
    def post(self, request):
        form = AgainEmailConfirmationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = UserProfile.objects.get(email=email)
                if not user.password:
                    if check_email_spam(email):
                        current_site = get_current_site(request)
                        mail_subject = 'اکانت خود را تایید کنید.'
                        message = render_to_string('auth/acc_active_email.html', {
                            'user': user,
                            'domain': current_site.domain,
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'token': account_activation_token.make_token(user),
                        })
                        to_email = form.cleaned_data.get('email')
                        send_email.delay(mail_subject, message, to_email)
                        return HttpResponse('لطفا ایمیل خود را تایید کنید.')
                    else:
                        return HttpResponse("ما قبلا به شما ایمیل ارسال کردیم، برای جلوگیری از اسپم لطفا 3 دقیقه صبر کنید و. دوباره تلاش کنید.")
                else:
                    return HttpResponse("پسورد برای شما ثبت شده است.")
            except UserProfile.DoesNotExist:
                return HttpResponse("اکانت شما وجود ندارد!")


class ActivateUserEmailView(generic.View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            # activate user and login:
            user.is_active = True
            user.save()
            login(request, user)
            
            form = UserSetPassword()
            return render(request, 'auth/activation_complete.html', {'form': form})
            
        else:
            return HttpResponse('لینک منقضی شده است!')
            
    def post(self, request, uidb64, token):

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # form = PasswordResetForm(request.POST)
        form = UserSetPassword(request.POST)
        if form.is_valid():
            user = User.objects.get(pk=user.pk)
            # user.set_password(form.cleaned_data.get("raw_password"))
            raw_password = form.cleaned_data.get("raw_password")
            user.set_password(raw_password)
            user.save()
            update_session_auth_hash(request, user)
            return redirect('account:dashboard')
        else:
            return render(request, 'auth/activation_complete.html', {'form': UserSetPassword()})


class DashboardView(LoginRequiredMixin, generic.View):
    login_url = 'account:login'
    
    def get(self, request):
        user = get_object_or_404(UserProfile, pk=request.user.pk)
        challenge = ChallengeEvent.objects.last()
        challenge_count = ChallengeEvent.objects.count()
        views_count = ViewsMid.objects.count()
        last_mounth = datetime.today() - timedelta(days=30)
        today = datetime.today()
        last_week = datetime.today() - timedelta(days=7)
        mounth_views_count = Article.objects.filter(published='p').annotate(
            count=Count("hits", filter=Q(articlehit__date_cr__gt=last_mounth))
        ).count()
        week_views_count = Article.objects.filter(published='p').annotate(
            count=Count("hits", filter=Q(articlehit__date_cr__gt=last_week))
        ).count()
        today_views_count = Article.objects.filter(published='p').annotate(
            count=Count("hits", filter=Q(articlehit__date_cr=today))
        ).count()
        articles_count = Article.objects.count()
        authors = UserProfile.objects.filter(is_author=True).count()
        admins = UserProfile.objects.filter(is_superuser=True).count()
        users = UserProfile.objects.filter(is_author=False, is_superuser=False, is_active=True).count()
        if self.request.user.is_superuser:
            articles = Article.objects.order_by("-title")[:5]
        elif self.request.user.is_author:
            articles = Article.objects.filter(author=self.request.user)
        elif not self.request.user.is_superuser and not self.request.user.is_author and \
                self.request.user.is_authenticated and self.request.user.is_active:
            articles = []
            article = Article.objects.all()
            for i in article:
                for x in i.likes.all():
                    if x.user == self.request.user:
                        articles.append(i)
        notifs = NotificationAdminCenter.objects.all()
        
        if request.user.is_superuser:
            comments = Comment.objects.order_by('-published')

        elif request.user.is_author:
            comments = []
            commentz = Comment.objects.all()
            for i in commentz:
                if i.from_user == self.request.user or i.to_article.author == self.request.user:
                    comments.append(i)

        else:
            comments = []
            commentz = Comment.objects.all()
            for i in commentz:
                if i.from_user == self.request.user:
                    comments.append(i)

        context = {
            'user': user,
            'challenge': challenge,
            'chc': challenge_count,
            'vc': views_count,
            'tvc': today_views_count,
            'mvc': mounth_views_count,
            'wvc': week_views_count,
            'ac': articles_count,
            'auc': authors,
            'adc': admins,
            'uc': users,
            'notifs': notifs,
            'articles': articles,
            'comments': comments,
        }
        return render(request, 'users/user-dashboard.html', context)

    def post(self, request):
        if not request.user.is_superuser:
            query = request.POST.get("q")
            result = Article.objects.filter(Q(title__icontains=query) |
                                            Q(text__icontains=query) |
                                            Q(published__icontains=query) |
                                            Q(category__title__icontains=query), author=request.user)
        else:
            query = request.POST.get("q")
            result = Article.objects.filter(Q(title__icontains=query) |
                                            Q(text__icontains=query) |
                                            Q(published__icontains=query) |
                                            Q(category__title__icontains=query) |
                                            Q(author__username__icontains=query))

        return render(request, 'dashboard-search.html', {'result': result})


class LikedArticles(LoginRequiredMixin, generic.ListView):
    model = Article
    context_object_name = 'all_posts'
    template_name = 'users/liked_posts.html'

    def get_queryset(self):
        l = []
        articles = Article.objects.all()
        for i in articles:
            for x in i.likes.all():
                if x.user == self.request.user:
                    l.append(i)
        return l


class AdministratorUsersManagerView(SuperUserMixinRequired, generic.ListView):
    context_object_name = 'users'
    template_name = 'users/admin-user-management.html'

    def get_queryset(self):            
        return UserProfile.objects.order_by('last_login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context


class UpdateUserProfileView(IsSelfOr404Mixin, generic.UpdateView): 
    model = UserProfile
    form_class = UpdateUserAccountForm
    success_url = reverse_lazy('account:dashboard')
    template_name = 'users/update-user.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        
    
class DeleteUserAccountProfileView(IsSelfOr404Mixin, generic.DeleteView):
    model = UserProfile 
    success_url = reverse_lazy('account:dashboard')
    template_name = 'users/delete-user.html'


class CreateContactView(IsAuthorOrSuperUserOr404, ContactCreateFormMixin, generic.CreateView):
    form_class = CreateUserContactsForm
    model = ContactsUser
    success_url = reverse_lazy('account:dashboard')
    template_name = 'users/create-user-contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class UpdateContactView(IsContactCreatorOr404Mixin, generic.UpdateView): 
    model = ContactsUser
    success_url = reverse_lazy('account:dashboard')
    form_class = UpdateUserContactsForm
    template_name = 'users/update-user-contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class DeleteContactView(IsContactCreatorOr404Mixin, generic.DeleteView): 
    model = ContactsUser
    success_url = reverse_lazy('account:dashboard')
    template_name = 'users/delete-user-contact.html'


class ContactsView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'contacts'
    template_name = 'users/admin-user-contacts.html'

    def get_queryset(self):
        self.contacts = ContactsUser.objects.filter(user=self.request.user)
        return self.contacts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class CreateArticleView(IsAuthorOrSuperUserOr404, ArticleCreateFormMixin, generic.CreateView): 
    model = Article
    form_class = CreateArticleForm
    success_url = reverse_lazy('account:articles')
    template_name = 'articles/create-article.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class ListArticleView(LoginRequiredMixin, generic.ListView):
    context_object_name = 'all_posts'
    template_name = 'articles/admin-or-user-article.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            self.all_posts = Article.objects.order_by('-published')
            return self.all_posts
        elif self.request.user.is_author:
            self.posts_I_created = Article.objects.filter(author=self.request.user)
            return self.posts_I_created
        elif not self.request.user.is_superuser and not self.request.user.is_author and \
                self.request.user.is_authenticated and self.request.user.is_active:
            l = []
            articles = Article.objects.all()
            for i in articles:
                for x in i.likes.all():
                    if x.user == self.request.user:
                        l.append(i)
            return l

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class DetailArticlePreView(ArticlePreviewMixin, generic.DetailView):
    template_name = 'articles/article-preview.html'
    context_object_name = 'article'

    def get_object(self,):
        if not self.request.user.is_superuser:
            article = Article.objects.get(pk=self.kwargs['pk'])
            if article.published == 'd' or article.published == 'b':
                return article
            else:
                raise Http404
        else:
            return Article.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.order_by('-title')[:5]
        context['last_articles'] = Article.objects.order_by('-title')[:5]
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class UpdateArticleView(IsArticleCreatorOr404Mixin, generic.UpdateView):
    model = Article
    form_class = UpdateUserArticleForm
    success_url = reverse_lazy('account:articles')
    template_name = 'articles/update-article.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user
        })
        return kwargs

    def get_object(self,):
        if not self.request.user.is_superuser:
            article = Article.objects.get(pk=self.kwargs['pk'])
            if article.published == 'd' or article.published == 'b':
                return article
            else:
                raise Http404
        else:
            return Article.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context

    def get_success_url(self) -> str:
        url = force_text(self.success_url)
        return url
    
    def form_valid(self, form):
        article = form.save()
        article.send_to_channel_f()
        return HttpResponseRedirect(self.get_success_url())


class DeleteArticleView(IsArticleCreatorOr404Mixin, generic.DeleteView):
    model = Article
    success_url = reverse_lazy('account:articles')
    template_name = 'articles/delete-article.html'


class CommentManagement(LoginRequiredMixin, generic.ListView):
    model = Comment
    context_object_name = 'comments'
    template_name = 'comments/admin-view.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            comments = Comment.objects.order_by('-published')
            return comments

        elif self.request.user.is_author:
            l = []
            comments = Comment.objects.all()
            for i in comments:
                if i.from_user == self.request.user or i.to_article.author == self.request.user:
                    l.append(i)
            return l

        else:
            l = []
            comments = Comment.objects.all()
            for i in comments:
                if i.from_user == self.request.user:
                    l.append(i)
            return l

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class CommentPublisher(SuperUserMixinRequired, generic.UpdateView):
    def dispatch(self, request, pk, *args, **kwargs):
        get_object_or_404(Comment, pk=pk)
        return super().dispatch(request, *args, **kwargs)

    model = Comment
    template_name = 'comments/comment-publisher-admin.html'
    fields = ['title', 'from_user', 'to_article', 'published']
    success_url = reverse_lazy('account:comments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class CreateChallengeView(SuperUserMixinRequired, generic.CreateView):
    model = ChallengeEvent
    fields = [  
                'title',
                'slug',
                'info',
                'image',
                'author',
                'category',
                'expr_date'
            ]
    success_url = 'account:challenges'
    template_name = 'challenges/admin-create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class UpdateChallengeView(SuperUserMixinRequired, generic.UpdateView):
    model = ChallengeEvent
    fields = [  
                'title',
                'slug',
                'info',
                'image',
                'author',
                'category',
                'expr_date'
            ]
    success_url = 'account:challenges'
    template_name = 'challenges/admin-update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class DeleteChallengeView(SuperUserMixinRequired, generic.DeleteView):
    model = ChallengeEvent
    success_url = 'account:challenges'
    template_name = 'challenges/admin-delete.html'


class ChallengesView(generic.ListView):
    model = ChallengeEvent
    fields = ['__all__']
    queryset = ChallengeEvent.objects.all()
    template_name = 'challenges/challenges.html'
    context_object_name = 'challenges'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class NotificationCreator(SuperUserMixinRequired, generic.CreateView):
    model = NotificationAdminCenter
    form_class = NotificationCreatorForm
    success_url = reverse_lazy('account:notifs-admin')
    template_name = 'notifications/admin-notif-creator.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class AllNotifications(SuperUserMixinRequired, generic.ListView):
    context_object_name = "notifs"
    model = NotificationAdminCenter
    template_name = 'notifications/admin-notifs.html'

    def get_queryset(self):
        return NotificationAdminCenter.objects.all()


class MyMessages(LoginRequiredMixin, generic.ListView):
    context_object_name = 'messages'
    model = Message
    template_name = 'messages/messages.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(Q(from_user=self.request.user) | Q(to_user=self.request.user))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class CreateMessage(SuperUserMixinRequired, generic.CreateView):
    form_class = MessageForm
    model = Message
    success_url = reverse_lazy('account:messages')
    template_name = 'messages/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class DeleteMessage(SuperUserMixinRequired, generic.DeleteView):
    model = Message
    success_url = reverse_lazy('account:messages')
    template_name = 'messages/message-delete.html'
    

class MessageUpdate(SuperUserMixinRequired, generic.UpdateView):
    model = Message
    success_url = reverse_lazy('account:messages')
    template_name = 'messages/message-update.html'
    fields = [
        'title',
        'from_user',
        'to_user',
        'read',
        'text',
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        
    def get_object(self):
        if self.request.user.is_superuser:
            return get_object_or_404(Message, pk=self.kwargs['pk'])
        else:
            raise Http404


class MessageDetail(generic.DetailView, LoginRequiredMixin):
    model = Message
    context_object_name = 'message'
    template_name = 'messages/message-detail.html'
    
    def get_object(self):
        return get_object_or_404(Message, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class DeleteNotif(SuperUserMixinRequired, generic.DeleteView):
    model = NotificationAdminCenter
    success_url = reverse_lazy('account:notifs-admin')
    template_name = 'notifications/delete-notif.html'


class CategoryAdminManagement(SuperUserMixinRequired, generic.ListView):
    model = Category
    context_object_name = 'categories'
    queryset = Category.objects.all()
    template_name = 'categories/admin-categories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class CategoryCreate(SuperUserMixinRequired, generic.CreateView):
    model = Category
    fields = [
        'parent',
        'title',
        'color',
        'slug',
        'desc',
    ]
    template_name = 'categories/admin-create.html'
    success_url = reverse_lazy('account:categories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context


class CategoryUpdate(SuperUserMixinRequired, generic.UpdateView):
    model = Category
    fields = [
        'parent',
        'title',
        'color',
        'slug',
        'desc',
    ]
    template_name = 'categories/admin-update.html'
    success_url = reverse_lazy('account:categories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context


class CategoryDelete(SuperUserMixinRequired, generic.DeleteView):
    model = Category
    template_name = 'categories/admin-delete.html'
    success_url = reverse_lazy('account:categories')


class AdminUserCreation(SuperUserMixinRequired, generic.CreateView):
    model = UserProfile
    form_class = UserCreationForm
    template_name = 'users/admin-user-creation.html'
    success_url = reverse_lazy('account:users')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context


class DashboardSearchView(LoginRequiredMixin, generic.View):
    def get(self, request):
        query = request.GET.get("query")
        if self.request.user.is_superuser:
            all_posts = Article.objects.filter(Q(title__icontains=query) | Q(text__icontains=query))
        elif self.request.user.is_author:
            all_posts = Article.objects.filter(Q(title__icontains=query) | Q(text__icontains=query), author=self.request.user)
        elif not self.request.user.is_superuser and not self.request.user.is_author and \
                self.request.user.is_authenticated and self.request.user.is_active:
            all_posts = []
            articles = Article.objects.filter(Q(title__icontains=query) | Q(text__icontains=query))
            for i in articles:
                for x in i.likes.all():
                    if x.user == self.request.user:
                        all_posts.append(i)

        return render(request, 'users/search.html', {'all_posts': all_posts})        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifs'] = NotificationAdminCenter.objects.all()
        return context
        

class ViewsDetailPage(SuperUserMixinRequired, generic.ListView):
    model = ViewsMid
    queryset = ViewsMid.objects.all()
    context_object_name = 'views'
    template_name = 'users/views.html'


class ChartSystem(SuperUserMixinRequired, generic.View):
    def get(self, request):
        authors = UserProfile.objects.filter(is_author=True).count()
        views = ViewsMid.objects.count()
        users = UserProfile.objects.filter(is_author=False, is_active=True).count()
        articles = Article.objects.filter(published="p").count()
        notifs = NotificationAdminCenter.objects.all()

        context = {
            'ac': authors,
            'vc': views,
            'uc': users,
            'pc': articles,
            'notifs': notifs
        }
        return render(request, 'users/admin-chart-system.html', context)


def validate_username(request):
    username = request.GET.get('username', None)
    response = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(response)

                
def validate_email(request):
    email = request.GET.get('email', None)
    reg_validator = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    # reg_validator = "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    if not UserProfile.objects.filter(email=email).exists():
        if re.match(reg_validator, email):
            response = {
                'correct': True
            }
        else:
            response = {
                'correct': False
            }
    else:
        response = {
            'taken': True
        }
        
    return JsonResponse(response)


def login_password_matches(request):
    raw_password = request.GET.get("raw_password")
    password_confirm = request.GET.get("password_confirm")
    print(raw_password)
    print(password_confirm)
    if raw_password != password_confirm:
        return JsonResponse({
            'not_match': True
        })
    else:
        return JsonResponse({
            'match': True,
        })
    

def notification_read_ajax(request):
    read = request.POST.get("pk")
    if read:
        notif = NotificationAdminCenter.objects.get(pk=read)
        notif.read = request.user
        notif.save()
        return JsonResponse({
            'read': True,
        })
    else:
        return JsonResponse("Error")


def ajax_slug_validators(request):
    category = request.GET.get("category_slug")
    article = request.GET.get("article_slug")
    challenge = request.GET.get("challenge_slug")

    if category:
        obj = Category.objects.filter(slug_iexact=category).exists()
        if obj:
            return JsonResponse({
                "is_taken": True
            })
    if article:
        obj = Article.objects.filter(slug_iexact=article).exists()
        if obj:
            return JsonResponse({
                "is_taken": True
            })
    if challenge:
        obj = ChallengeEvent.objects.filter(slug_iexact=category).exists()
        if obj:
            return JsonResponse({
                "is_taken": True
            })
    else:
        return JsonResponse({
            'result': None,
        })


def ajax_author_req(request):
    if request.is_ajax and request.method == "POST":
        admin = UserProfile.objects.get(is_superuser=True)
        user = UserProfile.objects.get(pk=request.POST.get("id"))
        if user.is_active and not user.is_superuser and not user.is_author:
            Message.objects.create(from_user=user, to_user=admin, title='درخواست نویسندگی', text='بنده میخواهم در وبسایت شما نویسندگی کنم', )
            return JsonResponse({
                'success': True,
            })
        else:
            return JsonResponse({
                'permissionError': True,
            })


def article_wrote(request, pk):
    
    a = Article.objects.get(pk=pk)
    a.published = 'i'
    a.save()
    return redirect('account:articles')


def ajax_delete_article(request):
    if request.is_ajax and request.method == "POST":
        uid = request.POST.get("id")
        print(uid)
        article = Article.objects.get(pk=uid)
        if article.author == request.user or request.user.is_superuser:
            article.delete()
            return JsonResponse({
                'success': True,
            })
        else:
            return JsonResponse({
                'permissionError': True,
            })


def ajax_delete_user(request):
    if request.is_ajax and request.method == "POST" and request.user.is_superuser:
        uid = request.POST.get("id")
        x = UserProfile.objects.get(pk=uid)
        x.delete()
        return JsonResponse({
            'success': True,
        })


def ajax_delete_user_contact(request):
    if request.is_ajax and request.method == "POST":
        uid = request.POST.get("id")
        cu = ContactsUser.objects.get(pk=uid)
        if cu.user == request.user or request.user.is_superuser:
            cu.delete()
            return JsonResponse({
                'success': True,
            })
        else:
            return JsonResponse({
                "permissionError": True
            })


def ajax_delete_category(request):
    if request.is_ajax and request.method == "POST" and request.user.is_superuser:
        uid = request.POST.get("id")
        c = Category.objects.get(pk=uid)
        c.delete()
        return JsonResponse({
            'success': True,
        })


def ajax_delete_notifs(request):
    if request.is_ajax and request.method == "POST" and request.user.is_superuser:
        uid = request.POST.get("id")
        x = NotificationAdminCenter.objects.get(pk=uid)
        x.delete()
        return JsonResponse({
            'success': True,
        })


def ajax_delete_messages(request):
    if request.is_ajax and request.method == "POST" and request.user.is_superuser:
        uid = request.POST.get("id")
        print(uid)

        c = Message.objects.get(pk=uid)
        c.delete()
        return JsonResponse({
            'success': True,
        })


def ajax_delete_challenges(request):
    if request.is_ajax and request.method == "POST" and request.user.is_superuser:
        uid = request.POST.get("id")
        z = ChallengeEvent.objects.get(pk=uid)
        z.delete()
        return JsonResponse({
            'success': True,
        })


def ajax_delete_comment(request):
    if request.is_ajax and request.method == "POST":
        uid = request.POST.get("id")
        comment = Comment.objects.get(pk=uid)
        if comment.from_user == request.user or request.user.is_superuser:
            comment.delete()
            return JsonResponse({
                'success': True
            })
        else:
            return JsonResponse({
                'permissionError': True,
            })

def ajax_delete_view(request):
    if request.is_ajax and request.method == "POST":
        uid = request.POST.get("id")
        try:
            view = ViewsMid.objects.get(pk=uid)
            view.delete()
            return JsonResponse({
                    'success': True
                })
        except ViewsMid.DoesNotExist:
            return JsonResponse({
                'error': 500,
            })


def ajax_delete_like(request):
    if request.is_ajax and request.method == "POST":
        uid = request.POST.get("id")
        like = Likes.objects.get(uid)
        if like.user == request.user:
            like.delete()
            return JsonResponse({
                'success': True
            })
        else:
            return JsonResponse({
                'permissionError': True
            })
