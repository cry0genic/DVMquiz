from django.urls import path
from . import views
import re
from django.conf.urls import url, include

urlpatterns = [
    path("", views.index, name="index"),
    path("instructions/", views.instructions, name="instructions"),
    path("get_no_of_questions/", views.get_no_of_questions, name="get_no_of_questions"),
    path("get_question/<int:queskey>/", views.get_question, name="get_question"),
    path("get_score/", views.get_score, name="get_score"),
    path("get_time_remaining/", views.get_time_remaining, name="get_time_remaining"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("sign_in/", views.sign_in, name="sign_in"),
    path("store_response/", views.store_response, name="store_response"),
    path("get_leaderboard/", views.get_leaderboard, name="leaderboard"),
    path("atr/", views.add_to_review, name="add_to_review"),
    path("atna/", views.add_to_not_attempted, name="add_to_not_attempted"),
    path("ata/", views.add_to_attempted, name="add_to_attempted"),
    path("atar/", views.add_to_ar, name="add_to_ar"),
    path("gqs/", views.get_question_status, name="get_question_status"),
    #path("add_question/", views.add_question, name="add_question"),
    path("add_team_member/", views.add_team_member, name="add_team_member"),
    path("delete_response/", views.delete_response, name="delete_response"),
    path("submitquiz/", views.submit, name="submit_quiz"),
    path('memcreate/', views.create_member, name="create_member"),
    path('logout/', views.sign_out, name="logout"),
    path('set_uncertainty/', views.set_uncertainty, name="set_uncertainty"),
    path('generate_questions/', views.generate_questions, name='generate_questions'),
    path('get_ques_attempted/', views.get_ques_attempted, name='get_ques_attempted'),
    path('get_result/', views.get_result, name="get_result"),
    
]