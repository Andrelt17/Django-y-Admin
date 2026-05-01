from django.urls import path
from . import views, views_auth

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('encomiendas/', views.encomienda_lista, name='encomienda_lista'),
    path('encomiendas/nueva/', views.encomienda_crear, name='encomienda_crear'),
    path('encomiendas/<int:pk>/', views.encomienda_detalle, name='encomienda_detalle'),
    path('login/', views_auth.login_view, name='login'),
    path('accounts/login/', views_auth.login_view),
    path('logout/', views_auth.logout_view, name='logout'),
    path('accounts/logout/', views_auth.logout_view),
    path('profile/', views_auth.profile, name='profile'),
    path('accounts/register/', views_auth.profile),
]
