from django.contrib import admin
from django.urls import path, include
from . import views
# from .views import YourModelListView

urlpatterns = [
    path('', views.home, name="home"),
    # path('student/', YourModelListView.as_view(), name='student'),
    # path('student_data/', views.post_student_data, name='student_data'),
    path('students_data/', views.get_students_data, name='students_data'),
    path('get_marks/', views.get_marks_data, name='marks_data'),
    path('get_marks_leader/', views.get_students_leader_marks, name='marks_leader'),
    path('get_student_daily/', views.get_student_daily, name='student_daily'),
]