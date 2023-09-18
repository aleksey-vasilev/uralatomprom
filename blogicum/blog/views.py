from django.core.paginator import Paginator
from django.utils.timezone import now
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import (get_object_or_404,
                              redirect)
from django.db.models import Count

from .models import Post, Category, User, Comment
from .constants import POST_PAGI_LENGTH
from .forms import UserForm, PostForm, CommentForm


class ProfileCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')


class GetPostMixin:
    def post_annotated(self, posts):
        post_list = posts.select_related(
            'author',
            'location',
            'category').annotate(comment_count=Count("comments"))
        return post_list

    def obj_paginator(self, post_list):
        paginator = Paginator(post_list, POST_PAGI_LENGTH)
        page_number = self.request.GET.get('page')
        return paginator.get_page(page_number)


class ProfileDetailView(GetPostMixin, DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_list = self.post_annotated(self.object.posts)
        if self.object != self.request.user:
            post_list = post_list.filter(
                is_published=True,
                pub_date__lte=now(),
                category__is_published=True
            )
        context['user'] = self.request.user
        context['profile'] = self.object
        context['page_obj'] = self.obj_paginator(
            post_list.order_by('-pub_date'))
        return context


class ProfileUpdateView(LoginRequiredMixin, GetPostMixin, UpdateView):
    template_name = 'blog/user.html'
    form_class = UserForm

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostListView(GetPostMixin, ListView):
    model = Post
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_list = self.post_annotated(self.object_list).filter(
            is_published=True,
            pub_date__lte=now(),
            category__is_published=True)
        context['page_obj'] = self.obj_paginator(
            post_list.order_by('-pub_date'))
        return context


class CategoryDetailView(GetPostMixin, DetailView):
    model = Category
    slug_url_kwarg = 'category_slug'
    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.object.is_published:
            raise Http404('Категория снята с публикации')
        post_list = self.post_annotated(self.object.posts).filter(
            is_published=True,
            pub_date__lte=now(),
            category__is_published=True)
        context['category'] = self.object
        context['page_obj'] = self.obj_paginator(
            post_list.order_by('-pub_date'))
        return context


class PostDetailView(GetPostMixin, DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        if (
            (self.object.author != self.request.user) and
            (not self.object.is_published)
        ):
            raise Http404('Пост снят с публикации')
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['page_obj'] = (
            self.obj_paginator(self.object.comments.select_related('author'))
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class AuthorPassMixin(UserPassesTestMixin):
    def test_func(self):
        return (self.get_object().author == self.request.user)


class PostMixin(AuthorPassMixin):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class CommentMixin(AuthorPassMixin):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.object.post.pk})

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.object.post.pk})


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm(instance=self.object)
        return context


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    pass
