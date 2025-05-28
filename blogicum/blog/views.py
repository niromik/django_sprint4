from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.views.generic.edit import UpdateView

from blog.models import Comment, Post, Category
from blog.forms import CommentForm, PostForm, ProfileForm

from functools import cached_property


User = get_user_model()


class PostListView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'
    ordering = ['-pub_date']

    def get_queryset(self):
        qs = super().get_queryset().filter(
            category__is_published=True,
            is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(comment_count=Count('comment'))
        return qs


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        post = get_object_or_404(
            Post,
            id=self.kwargs['id']
        )
        if self.request.user == post.author:
            return post

        if (
            post.is_published
            and post.pub_date <= timezone.now()
            and post.category.is_published
        ):
            return post
        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related('author')
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=[self.request.user]
        )


class PostEditView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect(
                'blog:post_detail',
                id=self.kwargs['id']
            )
        return super().dispatch(request, args, kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.kwargs['id']}
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect(
                'blog:post_detail',
                id=self.kwargs['id']
            )
        return super().dispatch(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=[self.request.user]
        )


class PostCategoriesView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/category.html'
    ordering = ['-pub_date']

    @cached_property
    def category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        qs = super().get_queryset().filter(
            category=self.category,
            is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(comment_count=Count('comment'))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileDetailView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/profile.html'
    ordering = ['-pub_date']

    @cached_property
    def owner(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        if self.request.user == self.owner:
            qs = super().get_queryset().filter(
                author=self.owner
            ).annotate(comment_count=Count('comment'))
        else:
            qs = super().get_queryset().filter(
                author=self.owner,
                is_published=True,
                pub_date__lte=timezone.now()
            ).annotate(comment_count=Count('comment'))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.owner
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=[self.request.user]
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    @cached_property
    def posting(self):
        return get_object_or_404(
            Post,
            pk=self.kwargs['id'],
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )

    def form_valid(self, form):
        """Save model instance."""
        form.instance.author = self.request.user
        form.instance.post = self.posting
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.posting.pk}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    pk_url_kwarg = 'comment'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect(
                'blog:post_detail',
                id=self.kwargs['id']
            )
        return super().dispatch(request, args, kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.kwargs['id']}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect(
                'blog:post_detail',
                id=self.kwargs['id']
            )
        return super().dispatch(request, args, kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.kwargs['id']}
        )
