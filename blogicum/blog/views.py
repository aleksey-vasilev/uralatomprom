from django.core.paginator import Paginator
from django.utils.timezone import now
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.shortcuts import (get_object_or_404,
                              render,
                              redirect)

from .models import Post, Category, User
from .constants import POST_PAGI_LENGTH
from .forms import UserForm

def create_post(request):
    pass

def add_comment(request, post_id):
    pass


def profile(request, username):
    profile = User.objects.get(username=username)
    post_list = profile.posts.order_by('id')
    paginator = Paginator(post_list, POST_PAGI_LENGTH)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)

def edit_profile(request):
    instance = get_object_or_404(User, username=request.user)
    form = UserForm(
        request.POST or None,
        instance=instance
    )
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile',username=form.cleaned_data['username'])
    return render(request, 'blog/user.html', context)


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
    ordering = '-pub_date'
    paginate_by = POST_PAGI_LENGTH
    template_name = 'blog/index.html'    


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related(
            'author',
            'location',
            'category'
        ), is_published=True,
        pub_date__lte=now(),
        category__is_published=True,
        pk=post_id
    )
    context = {
        'post': post,
    }
    return render(request, 'blog/detail.html', context)


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

    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(request, 'blog/category.html', context)
