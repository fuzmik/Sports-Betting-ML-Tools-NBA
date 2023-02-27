from django.urls import include, path

from . import views
from .views import GameListView
urlpatterns = [
    #path('', GameListView.as_view(), name='home-predict'),
    path('edit/<int:pk>/', views.editGame, name='edit-predict'),
    path('edit/<int:pk>/<str:change>', views.saveEdit, name='save-edit'),
    path('edit/<int:pk>/remove/<str:player>', views.removePlayer, name='remove-player'),

    path('new/<str:home>/<str:visitor>/<str:date>/', views.quickcreate, name='quick-create'),

    path('', GameListView.as_view() , name='home-predict'),
    path('date/<str:dateSelected>', GameListView.as_view() , name='home-predict'),
    path('#<int:pk>', views.getScore , name='get-score'),
    path('stats/', views.statsView , name='stats-view'),
    #path('predicttoday/', views.predictToday , name='predict-today'),


]
