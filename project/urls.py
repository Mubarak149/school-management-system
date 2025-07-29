
from django.conf.urls.static import static
from . import settings
from django.contrib import admin
from django.urls import path ,include
from student import views as studentviews
from school_admin import views as adminviews
from school_admin.views import SchoolNews, MyProfile, EditPost, DeletePost
from student.views import StudentProfile
from student import views as studentviews
from staff import views as staffviews
from staff.views import (StaffProfile, StudentGradesView, UpdateGradeScoreView)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include('main.urls')),
    path("finance/", include('finance.urls')),
    # admin url
    path('school-admin', adminviews.home, name='adminHome'),
    path('student-dld', adminviews.students_view, name='classRecord'),
    path("student-score", adminviews.students_term_score, name="studentScore"),
    path("new-admin", adminviews.add_new_admin, name="newAdmin"),
    path("del/<int:pk>/", adminviews.delete_student, name="Delete"),
    path("staff-del/<int:pk>/", adminviews.delete_staff, name="staffDelete"),
    path("admin-profile/<int:pk>/", MyProfile.as_view(), name="adminProfile"),
    path('edit-post/<int:pk>/', EditPost.as_view(), name='editPost'),
    path('delete-post/<int:pk>/', DeletePost.as_view(), name='deletePost'),
    path("teacher_del/<int:pk>/", adminviews.delete_teacher_obj, name="teacherDelete"),
    path("academic_session_management", adminviews.academic_session_management, name="academic_session_management"),
    path("add_academic_session", adminviews.academic_session_management, name="add_academic_session"),
    path('set_current_session/<int:id>/', adminviews.set_current_session, name='set_current_session'),
    #path("event", adminviews.event, name="event"),
    path("settings", adminviews.settings, name="adminSetting"),
    path("news", SchoolNews.as_view(), name="news"),
    path("new-student", adminviews.add_new_student, name="addNewStudent"),
    path('student-edit/<int:id>/', adminviews.edit_student, name='editStudent'),
    path("new-staff", adminviews.add_new_staff, name="addStaff"),
    path('staff-edit/<int:id>/', adminviews.edit_staff, name='editStaff'),
    path('new-teacher/<int:id>/', adminviews.add_teacher, name='addTeacher'),
    path('subjects/', adminviews.subject_list_create, name='subject_list_create'),
    path('subjects/<int:pk>/edit/', adminviews.subject_update, name='subject_update'),
    path('subjects/<int:pk>/delete/', adminviews.subject_delete, name='subject_delete'),
    path('classes/', adminviews.schoolclass_list, name='class_list'),
    path('classes/create/', adminviews.schoolclass_create, name='class_create'),
    path('classes/<int:pk>/update/', adminviews.schoolclass_update, name='class_update'),
    path('classes/<int:pk>/delete/', adminviews.schoolclass_delete, name='class_delete'),
    path('site-setting', adminviews.site_settings_view, name='site_settings'),
    path('gallery/manage/', adminviews.manage_gallery, name='manage_gallery'),
    path('gallery/edit/<int:pk>/', adminviews.edit_gallery_image, name='edit_gallery_image'),
    path('gallery/delete/<int:pk>/', adminviews.delete_gallery_image, name='delete_gallery_image'),
    path('notifications/', adminviews.manage_notifications, name='manage_notifications'),
    path('notifications/edit/<int:pk>/', adminviews.edit_notification, name='edit_notification'),
    path('notifications/delete/<int:pk>/', adminviews.delete_notification, name='delete_notification'),
    # end admin url
    
    # staff url 
    path("staff/<int:cls>/", staffviews.staffhome, name="staffHome"),
    path('staff-profile/<int:pk>/', StaffProfile.as_view(), name='viewStaff'),
    path("staff-setting/<int:id>/", staffviews.staff_setting , name="staffSetting"),
    path("update-student-grade-score/<int:pk>/", UpdateGradeScoreView.as_view(), name="updateStudentGrades"),
    path("student-grades/<int:pk>/", StudentGradesView.as_view(), name="studentGrades"),
    path("promote_students/<int:cls>/", staffviews.promotion_view, name="promote_students"),
    # end staff url
    
    
    # student url
    #path("student", studentviews.student_home, name="studentHome"),
    path('student-profile/<int:pk>/', StudentProfile.as_view(), name='viewStudent'),
    path("student-promotion-records/<int:id>/", studentviews.promotion_record_view, name="promotionRecords"),
    # end student url
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

