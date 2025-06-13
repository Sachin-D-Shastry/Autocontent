from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page_view, name='landing_page'),
    path('search-engine/', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('workflow/', views.workflow_view, name='workflow'),
    path('generate/', views.generate_view, name='generate'),
    path('convert_pdf/<int:article_id>/', views.convert_pdf, name='convert_pdf'),
    path('generate_from_image/', views.image_generate_view, name='generate_from_image'),
    path('recents/', views.recents, name='recents'),
    path('content/<int:content_id>/', views.open_content, name='open_content'),
    path('search/', views.search_view, name='search'),
    path('suggest/', views.suggest_keywords, name='suggest_keywords'),
    path('unauthorized/', views.unauthorized_view, name='unauthorized'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

]
