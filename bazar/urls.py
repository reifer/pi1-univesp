from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Páginas Públicas
    path('', views.index, name='index'),
    path('sobre/', views.sobre, name='sobre'),
    path('contato/', views.contato, name='contato'),

    # Doações
    path('doacoes/', views.doacoes_list, name='doacoes_list'),
    path('doacoes/<int:id>/', views.doacao_detalhe, name='doacao_detalhe'),
    path('doar/', views.cadastrar_doacao, name='cadastrar_doacao'),  # Novo: cadastro público
    path('doar/confirmacao/', views.doacao_confirmacao, name='doacao_confirmacao'),

    # Autenticação
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Admin/Painel (protegido)
    path('painel/', views.admin_dashboard, name='admin_dashboard'),
    path('painel/deletar/<int:pk>/', views.deletar_doacao, name='deletar_doacao'),
    path('painel/status/<int:pk>/', views.atualizar_status_doacao, name='atualizar_status_doacao'),
    path('painel/baixa/<int:pk>/', views.dar_baixa_doacao, name='dar_baixa_doacao'),
]