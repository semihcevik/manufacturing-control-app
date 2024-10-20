# departments/urls.py
from django.urls import path
from .views import DepartmentInfoView

urlpatterns = [
    path('department/list', DepartmentInfoView.as_view(), name='department-info'),
]
