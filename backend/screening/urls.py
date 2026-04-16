from django.urls import path
from . import views

urlpatterns = [
    path("sessions/", views.create_session, name="create-session"),
    path("sessions/<uuid:session_id>/", views.get_session, name="get-session"),
    path(
        "sessions/<uuid:session_id>/questions/",
        views.get_questions,
        name="get-questions",
    ),
    path(
        "sessions/<uuid:session_id>/answers/",
        views.submit_answers,
        name="submit-answers",
    ),
    path(
        "sessions/<uuid:session_id>/analyze/",
        views.analyze_session,
        name="analyze-session",
    ),
    path(
        "sessions/<uuid:session_id>/results/",
        views.get_results,
        name="get-results",
    ),
    path("providers/nearby/", views.nearby_providers, name="nearby-providers"),
]
