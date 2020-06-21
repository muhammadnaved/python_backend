from django.urls import path, include
from knox.views import LogoutView
from rest_framework import routers

from api import views
from api.views import LoginView, AccountView, CheckDBConnectionView

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'roles', views.RoleViewSet)
router.register(r'connection_types', views.ConnectionTypeViewSet)
router.register(r'connections', views.ConnectionViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path(r'auth/data/', AccountView.as_view()),
    path(r'auth/login/', LoginView.as_view()),
    path(r'auth/logout/', LogoutView.as_view()),
    path(r'configuration/', views.ConfigurationView.as_view()),
    path(r'csv/', views.CsvModelView.as_view()),
    path(r'load_ciso/', views.CisoDataView.as_view()),

    path(r'check_db_connection/', CheckDBConnectionView.as_view()),
]
