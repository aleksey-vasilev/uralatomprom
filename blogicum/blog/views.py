from django.core.paginator import Paginator
from django.utils.timezone import now
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (get_object_or_404,
                              render,
                              redirect)

from .models import Post, Category, User, Comment
from .constants import POST_PAGI_LENGTH
from .forms import UserForm, PostForm, CommentForm


class ProfileCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')


class PostMixin:
    def comment_count(self, obj):
        post_list = obj.select_related(
            'author',
            'location',
            'category')
        comment_counts = [None] * len(post_list)
        for i in range(len(post_list)):
            comment_counts[i] = post_list[i].comments.count()
        return comment_counts

    def post_paginator(self, post_list):
        paginator = Paginator(post_list, POST_PAGI_LENGTH)
        page_number = self.request.GET.get('page')
        return paginator.get_page(page_number)


class ProfileDetailView(PostMixin, DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_list = self.obj.select_related(
            'author',
            'location',
            'category')
        if self.object.username != self.request.user:
            post_list = post_list.filter(
                is_published=True,
                pub_date__lte=now(),
            )
        context['profile'] = self.object
        context['page_obj'] = self.post_paginator(post_list)
        context['post.comment_count'] = self.comment_count(post_list)
        return context


@login_required
def edit_profile(request):
    instance = get_object_or_404(User, username=request.user)
    form = UserForm(
        request.POST or None,
        instance=instance
    )
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=form.cleaned_data['username'])
    return render(request, 'blog/user.html', context)


class ProfileUpdateView(UpdateView):
    model = User
    template_name = 'blog/profile.html'
    form_class = UserForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_list = self.object.posts.select_related('author')
        if self.object.username != self.request.user:
            post_list = post_list.filter(
                is_published=True,
                pub_date__lte=now(),
            )
        paginator = Paginator(post_list, POST_PAGI_LENGTH)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['profile'] = self.object
        context['page_obj'] = page_obj
        return context


class PostListView(ListView):
    model = Post
    queryset = Post.objects.select_related(
        'author',
        'location',
        'category'
    ).filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True)
    paginate_by = POST_PAGI_LENGTH
    template_name = 'blog/index.html'


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug
    )
    post_list = category.posts.select_related(
        'author',
        'location',
    ).filter(
        is_published=True,
        pub_date__lte=now())
    paginator = Paginator(post_list, POST_PAGI_LENGTH)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if (instance.author != request.user) & (not instance.is_published):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostMixin:
    model = Post
    template_name = 'blog/create.html'


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):
    pk_url_kwarg = "post_id"

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['post_id'])
        self.form = PostForm(instance=instance)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=post_id)


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        self.comment = get_object_or_404(Comment,
                                         post=kwargs['post_id'],
                                         pk=kwargs['comment_id'],
                                         author=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'comment_id': self.comment.post.pk})


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    pass
