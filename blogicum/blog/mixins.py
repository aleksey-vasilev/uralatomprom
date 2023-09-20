from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Count
from django.core.paginator import Paginator

from .constants import POST_PAGI_LENGTH
from .models import Post, Comment
from .forms import PostForm, CommentForm


class PostToolsMixin:
    @staticmethod
    def post_annotated(posts):
        return posts.select_related(
            'author',
            'location',
            'category').annotate(
                comment_count=Count('comments')).order_by('-pub_date')

    def obj_paginator(self, post_list):
        paginator = Paginator(post_list, POST_PAGI_LENGTH)
        page_number = self.request.GET.get('page')
        return paginator.get_page(page_number)


class AuthorPassMixin(UserPassesTestMixin):
    def test_func(self):
        return (self.get_object().author == self.request.user)


class PostMixin(LoginRequiredMixin, AuthorPassMixin):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class CommentMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.object.post.pk})
