from django.urls import path 
from . import views


urlpatterns = [
    path("", views.main, name="main"),
    path("about", views.about, name="about"),
    path("gallery", views.gallery_view, name="gallery"),
    path("Staffs", views.staff_hierarchy, name="staffHierarchy"),
    #path("promotion-status", views.status, name="promotionStatus"),
    path("admission", views.admission, name="admission"),
    path("graduate", views.search_student_academic_view, name="graduateView"),
    path("logout", views.logout_view, name="logout"),
]

