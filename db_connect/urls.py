from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    path('', views.user_signup, name='user_signup'),
    path('login/', views.login_view, name='login_view'),
    path('role_manager/', views.role_manager, name='role_manager'),
    path('events/create/<int:user_id>', views.event_create, name='event_create'),
    path('collaboration_portal/<int:user_id>', views.collaboration_portal, name='collaboration_portal'),
    path('logout/', views.logout_view, name='logout_view'),
    path('chatroom/<str:room_name>/<int:user_id>', views.room, name='room'),

    #STUDENT PATHS
    path('student/<int:user_id>', views.student, name='student'),
    #path('my_events/<int:user_id>', views.my_events, name='my_events'),
    path('my_assignments/<int:user_id>', views.my_assignments, name='my_assignments'),
    path('my_schedule/<int:user_id>', views.my_schedule, name='my_schedule'),
    path('performance_report/<int:user_id>', views.performance_report, name='performance_report'),
    #path('my_events/<int:user_id>', views.my_events, name='my_events'),
    path('events/signup/<int:user_id>', views.event_signup, name='event_signup'),
    path('course_register/<str:A_number>/<int:extra>', views.register_courses, name='register_courses'),
    path('course_quantity/<str:A_number>', views.course_quantity, name='course_quantity'),
    #STUDENT PATHS (END)

    #TUTOR PATHS
    path('tutor/<int:user_id>', views.tutor, name='tutor'),
    path('assignment_manager/<int:user_id>', views.assignment_manager, name='assignment_manager'),
    path('performance_manager/<int:user_id>', views.performance_manager, name='performance_manager'),
    path('submit_feedback', views.submit_feedback, name='submit_feedback'),
    path('tutor_course/<str:Tid>', views.tutor_course, name='tutor_course'),
    #TUTOR PATHS (END)

    #MENTOR PATHS
    path('mentor/<int:user_id>', views.mentor, name='mentor'),
    path('meeting_scheduler/<int:user_id>', views.meeting_scheduler, name='meeting_scheduler'),
    path('performance_manager/<int:user_id>', views.performance_manager, name='performance_manager'),
    #MENTOR PATHS (END)
]
urlpatterns += staticfiles_urlpatterns()
