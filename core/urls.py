from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/edit/', views.project_edit, name='project_edit'),
    path('logout/', views.custom_logout, name='logout'),
    path('projects/<int:project_id>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:project_id>/items/create/', views.item_create, name='item_create'),
    path('items/<int:item_id>/edit/', views.item_edit, name='item_edit'),
    path('items/<int:item_id>/updates/delete/<str:timestamp>/', views.delete_update, name='delete_update'),
    path('api/item/<int:item_id>/update_next_step/', views.update_next_step, name='update_next_step'),
    path('items/<int:item_id>/delete_file/<str:timestamp>/', views.delete_item_file, name='delete_item_file'),

    # ✅ New AJAX endpoints
    path('projects/<int:project_id>/contacts/add/', views.add_contact, name='add_contact'),
    path('contacts/<int:contact_id>/delete/', views.delete_contact, name='delete_contact'),
    path('projects/<int:project_id>/update_info/', views.update_project_info, name='update_project_info'),
]
