from django.urls import path
from .import views

app_name = 'profiles'

urlpatterns = [
  path('', views.ProfileListView.as_view(), name='all-profiles'),
  path('myprofile/', views.myprofile, name='myprofile'),
  path('my-invites/', views.inivites_received, name='my-invites'),
  path('to-invite/', views.inivite_profiles_list, name='invite-profiles'),
  path('send-invite/', views.send_invitation, name='send-invite'),  
  path('remove-friend/', views.remove_from_friends, name='remove-friend'),
  path('my-invites/accept/', views.accept_invitation, name='accept-invite'),
  path('my-invites/reject/', views.reject_invitation, name='reject-invite'),
  path('<slug>/', views.ProfileDetailView.as_view(), name='profile-detail'),
]
