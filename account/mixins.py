from blog.models import Article
from account.models import ContactsUser, UserProfile
from django.http.response import Http404
from django.shortcuts import get_object_or_404


class SuperUserMixinRequired:

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return super(SuperUserMixinRequired, self).dispatch(request, *args, **kwargs)
            else:
                raise Http404
        raise Http404


class IsSelfOr404Mixin:

    def dispatch(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            user = get_object_or_404(UserProfile, pk=pk)
            if request.user == user or request.user.is_superuser:
                return super(IsSelfOr404Mixin, self).dispatch(request, pk, *args, **kwargs)
            else:
                raise Http404
        raise Http404


class IsContactCreatorOr404Mixin:

    def dispatch(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            contact = get_object_or_404(ContactsUser, pk=pk)
            if contact.user == request.user and request.user.is_author or request.user.is_superuser:
                return super(IsContactCreatorOr404Mixin, self).dispatch(request, pk, *args, **kwargs)
            else:
                raise Http404
        raise Http404


class ContactCreateFormMixin:

    def form_valid(self, form):
        self.contact = form.save(commit=False)
        self.contact.user = self.request.user
        self.contact.save()
        return super(ContactCreateFormMixin, self).form_valid(form)


class IsArticleCreatorOr404Mixin:

    def dispatch(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            article = get_object_or_404(Article, pk=pk)
            if article.author == request.user or request.user.is_superuser:
                return super(IsArticleCreatorOr404Mixin, self).dispatch(request, pk, *args, **kwargs)
            else:
                raise Http404
        raise Http404

class IsAuthorOrSuperUserOr404:

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_author or request.user.is_superuser:
                return super(IsAuthorOrSuperUserOr404, self).dispatch(request, *args, **kwargs)
            else:
                return Http404
        raise Http404

class ArticleCreateFormMixin:

    def form_valid(self, form):
        self.article = form.save(commit=False)
        self.article.author = self.request.user
        self.article.published = 'd'
        self.article.save()
        return super(ArticleCreateFormMixin, self).form_valid(form)


class ArticlePreviewMixin:

    def dispatch(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            article = get_object_or_404(Article, pk=pk)
            if article.author == request.user or request.user.is_superuser\
                    and article.published == 'd' or article.published == 'b':
                return super(ArticlePreviewMixin, self).dispatch(request, pk, *args, **kwargs)
            else:
                raise Http404
        raise Http404
