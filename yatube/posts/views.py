from django.conf import settings as st
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.select_related('group').all()
    paginator = Paginator(post_list, st.PАGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    context = {
        'posts': post_list,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, st.PАGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=author)
    count_user_posts = user_posts.count()
    paginator = Paginator(user_posts, st.PАGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = None
    template = 'posts/profile.html'
    context = {
        'author': author,
        'post_count': count_user_posts,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    count = Post.objects.filter(author_id=post.author).count()
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'form': form,
        'post': post,
        'count': count,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', post.author)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save()
        return redirect('posts:post_detail', post.id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, template, context)


@login_required
def post_delete(request, post_id):
    template = 'posts/delete_post.html'
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('posts:profile', post.author)
    return render(request, template, {'item': post})


@login_required
def add_comment(request, post_id):
    template = 'posts:post_detail'
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(template, post_id=post_id)


@login_required
def follow_index(request):
    """Посты авторов, на которых подписан текущий пользователь.
    """
    news = Post.objects.filter(
        author__following__user=request.user
    ).order_by('-pub_date')
    paginator = Paginator(news, st.PАGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Лента избранного'
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """ Функция подписки на автора.
    """
    user = request.user
    following = get_object_or_404(User, username=username)
    if (
        following == request.user
        or Follow.objects.get_or_create(author=following, user=request.user)
    ):
        return redirect('posts:profile', username=username)
    Follow.objects.create(user=user, author=following)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """ Функция отписки от автора.
    """
    user = request.user
    follower = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=user, author=follower)
    follow.delete()
    return redirect('posts:profile', username=username)
