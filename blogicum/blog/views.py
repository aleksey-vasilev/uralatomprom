from django.utils.timezone import now
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from .constants import POST_PAGI_LENGTH
from .models import Post, Category, User, Comment
from .forms import UserForm, PostForm, CommentForm
from .mixins import PostToolsMixin, AuthorPassMixin, PostMixin


class ProfileCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')


class ProfileDetailView(PostToolsMixin, DetailView):
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
        context['profile'] = self.object
        context['page_obj'] = self.obj_paginator(post_list)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    form_class = UserForm

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class CategoryDetailView(PostToolsMixin, DetailView):
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
        context['page_obj'] = self.obj_paginator(post_list)
        return context


class PostListView(PostToolsMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    queryset = PostToolsMixin.post_annotated(
        Post.objects.filter(is_published=True,
                            pub_date__lte=now(),
                            category__is_published=True))
    paginate_by = POST_PAGI_LENGTH


class PostDetailView(PostToolsMixin, DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        if ((self.object.author != self.request.user
             ) and (not self.object.is_published)):
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


class PostUpdateView(PostMixin, UpdateView):
    pass


class PostDeleteView(PostMixin, DeleteView):
    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class CommentMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.object.post.pk})


class CommentCreateView(CommentMixin, CreateView):
    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)


class CommentUpdateView(AuthorPassMixin, CommentMixin, UpdateView):
    pass


class CommentDeleteView(AuthorPassMixin, CommentMixin, DeleteView):
    pass
