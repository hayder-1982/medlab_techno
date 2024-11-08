from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from . import api_views


urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('blog/post/', views.BlogCreateView.as_view(), name='post'),
    path('blog/<int:pk>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('blog/update/<int:pk>/', views.BlogUpdateView.as_view(), name='blog_update'),
    path('blog/updatetest/<int:pk>/', views.TestUpdateView.as_view(), name='test_update'),
    path('blog/delete/<int:pk>/', views.BlogDeleteView.as_view(), name='blog_delete'),
    path('blog/cbc/<str:idBarcode>/', views.CBCView, name='cbc'),

    path('blog/deletetest/<int:pk>/', views.TestDeleteView.as_view(), name='test_delete'),
    path('blog/pdfcbc/<int:idBarcode>/', views.generate_pdfcbc, name='generate_pdfcbc'),
    path('blog/pdfresult/<int:idBarcode>/', views.generate_pdfresult, name='generate_pdfresult'),

    # API
    path('api/like-toggle/', api_views.LikeToggleAPIView.as_view(), name='like-toggle'),
    path('api/blog/<int:blog_id>/comment/', api_views.CommentCreateAPI.as_view(), name='create_comment_api'),
    path('api/blog/<int:blog_id>/result/', api_views.resultCreateAPI.as_view(), name='create_result_api'),

    # Authentication URLs
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
]
