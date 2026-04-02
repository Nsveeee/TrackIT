from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('report/', views.report_bug, name='report'),
    path('update/<int:id>/', views.update_status, name='update'),
    path('comment/<int:id>/', views.add_comment, name='comment'),
    # Use "manage/" to avoid clashing with Django's built-in /admin/ site.
    path('manage/assign/<int:id>/', views.admin_assign_bug, name='admin_assign_bug'),
    path('manage/delete/<int:id>/', views.admin_delete_bug, name='admin_delete_bug'),
    path('manage/project/create/', views.admin_create_project, name='admin_create_project'),
    path('manage/project/edit/<int:id>/', views.admin_edit_project, name='admin_edit_project'),
    path('manage/project/delete/<int:id>/', views.admin_delete_project, name='admin_delete_project'),
    path('manage/project/<int:id>/developers/', views.admin_update_project_devs, name='admin_update_project_devs'),
]