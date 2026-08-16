from django.urls import path

from . import views

app_name = "profile_site"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
    path("clients/", views.clients, name="clients"),
    path("team/", views.team, name="team"),
    path("team/<slug:slug>/", views.team_detail, name="team_detail"),
    path("insights/", views.insights, name="insights"),
    path("insights/<slug:slug>/", views.insight_detail, name="insight_detail"),
    path("contact/", views.contact, name="contact"),
    path("contact/received/", views.enquiry_received, name="enquiry_received"),
]
