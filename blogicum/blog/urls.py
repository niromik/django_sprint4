from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views


app_name = 'blog'

urlpatterns = [
    path('',
         views.PostListView.as_view(), name='index'),

    path('posts/create/',
         views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:id>/',
         views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:id>/edit/',
         views.PostEditView.as_view(), name='edit_post'),
    path('posts/<int:id>/delete/',
         views.PostDeleteView.as_view(), name='delete_post'),

    path('category/<slug:category_slug>/',
         views.PostCategoriesView.as_view(), name='category_posts'),

    path('profile/<str:username>/',
         views.ProfileDetailView.as_view(), name='profile'),
    path('user/',
         views.ProfileEditView.as_view(), name='edit_profile'),

    path('posts/<int:id>/comment/',
         views.CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:id>/edit_comment/<int:comment>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:id>/delete_comment/<int:comment>/',
         views.CommentDeleteView.as_view(), name='delete_comment')
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
