from django.contrib import admin
from django.urls import path
from cloudstorage import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard + File actions
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_file, name='upload_file'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),

    # Sharing
    path('share/<str:token>/', views.shared_file, name='shared_file'),
]