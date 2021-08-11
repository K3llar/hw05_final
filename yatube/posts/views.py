from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from yatube.settings import paginator_pages


def paginator(request, post_list, paginator_pages):
    paginator_object = Paginator(post_list, paginator_pages)
    page_number = request.GET.get('page')
    page = paginator_object.get_page(page_number)
    return page


@require_GET
def index(request):
    post_list = cache.get('index_page')
    if post_list is None:
        post_list = Post.objects.select_related('group').all()
        cache.set('index_page', post_list, timeout=20)
    return render(request, 'posts/index.html',
                  {'page': paginator(
                      request,
                      post_list,
                      paginator_pages
                  )})
# Как я понял из описания select_related нужен для уменьшения количества запросов
# к базе. В случае когда запрос вызывает не все элементы как в функции index
# В случаях когда запрос содержит фильтрацию по какому либо элементу
# (автор, группа) нет же смысла использовать select_related?


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.groups.all()
    return render(request, 'posts/group.html',
                  {'group': group,
                   'page': paginator(
                       request,
                       post_list,
                       paginator_pages
                   )})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.all().filter(author=author)
    if request.user.is_authenticated and Follow.objects.filter(
            user=request.user, author=author).exists():
        return render(request, 'posts/profile.html',
                      {
                          'author': author,
                          'page': paginator(
                              request,
                              post_list,
                              paginator_pages
                          ),
                          'following': True,
                      })
    return render(request, 'posts/profile.html',
                  {
                      'author': author,
                      'page': paginator(
                          request,
                          post_list,
                          paginator_pages
                      ),
                  })


def post_view(request, username, post_id):
    author = User.objects.get(username=username)
    post = Post.objects.all().filter(author=author).get(pk=post_id)
    form = CommentForm(request.POST or None)
    comment = Comment.objects.all()
    return render(request, 'posts/post.html',
                  {
                      'author': author,
                      'post': post,
                      'form': form,
                      'comments': comment,
                  })


@login_required()
def new_post(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        new = form.save(commit=False)
        new.author = User.objects.get(username=request.user.username)
        new.save()
        return redirect('index')
    return render(request, 'posts/new_post.html',
                  {'form': form, })


@login_required()
def edit_post(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = get_object_or_404(User, username=username)
    if request.user != post.author:
        return redirect(f'/{post.author}/{post_id}/')
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid() and post.author == author:
        post = form.save(commit=False)
        post.author = User.objects.get(username=username)
        post.save()
        return redirect(f'/{post.author}/{post_id}/')
    return render(request, 'posts/new_post.html',
                  {
                      'form': form,
                      'post': post,
                      'edit': True,
                  })


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required()
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect(f'/{post.author}/{post_id}/')
    return render(request,
                  'posts/comments.html',
                  {'form': form}, )


@login_required()
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user_name = request.user.username
    user = get_object_or_404(User, username=user_name)
    if author != user and not Follow.objects.filter(
            author=author,
            user=request.user
    ).exists():
        Follow.objects.create(
            user_id=request.user.id,
            author_id=author.id
        )
    return redirect('profile', username)


@login_required()
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = get_object_or_404(User, username=request.user)
    status = Follow.objects.filter(user=user, author=author)
    if status.exists():
        status.delete()
    return redirect('profile', username)


@login_required()
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    return render(request,
                  'posts/follow.html',
                  {'page': paginator(request,
                                     post_list,
                                     paginator_pages
                                     )})
