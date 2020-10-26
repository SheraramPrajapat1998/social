from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Relationship
from .forms import ProfileModelForm, UserRegistrationForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


def register(request):
  if request.method == 'POST':
    user_form = UserRegistrationForm(request.POST)
    if user_form.is_valid():
      # Create a new user object but avoid saving it yet
      new_user = user_form.save(commit=False)
      # Set the chosen password
      new_user.set_password(user_form.cleaned_data['password1'])
      # Save the User object
      new_user.save()
      return render(request, 'register_done.html', {'new_user': new_user})
  else:
    user_form = UserRegistrationForm()
    return render(request, 'register.html', {'user_form': user_form})


@login_required
def myprofile(request):
  profile = Profile.objects.get(user=request.user)
  form = ProfileModelForm(data=request.POST or None, files=request.FILES or None, instance=profile)

  if request.method == 'POST':
    if form.is_valid():
      form.save()
      messages.success(request, 'Your profile has been updated successfully!')

  context = {
    'profile': profile,
    'form': form,
  }
  return render(request, 'profiles/myprofile.html', context)


@login_required
def inivites_received(request):
  profile = Profile.objects.get(user=request.user)
  qs = Relationship.objects.invitations_received(profile)
  results = list(map(lambda x:x.sender, qs))
  is_empty = False
  if len(results) == 0:
    is_empty = False
  context = {
    'qs': results,
    'is_empty': is_empty
  }
  return render(request, 'profiles/my_invites.html', context)


@login_required
def accept_invitation(request):
  if request.method == 'POST':
    pk = request.POST.get('profile_pk')
    sender = Profile.objects.get(pk=pk)
    receiver = Profile.objects.get(user=request.user)
    rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
    if rel.status == 'send':
      rel.status = 'accepted'
      rel.save()
      messages.success(request, f"You and {sender.user} are now friends with each other.")
  return redirect('profiles:my-invites')

@login_required
def reject_invitation(request):
  if request.method == 'POST':
    pk = request.POST.get('profile_pk')
    receiver = Profile.objects.get(user=request.user)
    sender = Profile.objects.get(pk=pk)
    rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
    rel.delete()
    messages.info(request, f"You have rejected {sender.user}'s friend request")
  return redirect('profiles:my-invites')


@login_required
def inivite_profiles_list(request):
  user = request.user
  qs = Profile.objects.get_all_profiles_to_invite(user)

  context = {'qs':qs}
  return render(request, 'profiles/to_invite_list.html', context)


@login_required
def profiles_list(request):
  user = request.user
  qs = Profile.objects.get_all_profiles(user)
  context = {
    'qs': qs
  }
  return render(request, 'profiles/profile_list,html', context)


class ProfileDetailView(LoginRequiredMixin, DetailView):
  model = Profile
  template_name = 'profiles/detail.html'

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    user = User.objects.get(username__iexact=self.request.user)
    profile = Profile.objects.get(user=user)
    rel_r = Relationship.objects.filter(sender=profile)
    rel_s = Relationship.objects.filter(receiver=profile)
    rel_receiver = []
    rel_sender = []
    for item in rel_r:
      rel_receiver.append(item.receiver.user)
    for item in rel_s:
      rel_sender.append(item.sender.user)
    context['rel_receiver'] = rel_receiver
    context['rel_sender'] = rel_sender
    context['posts'] = self.get_object().get_all_authors_posts()
    context['len_posts'] = True if len(self.get_object().get_all_authors_posts()) > 0 else False
    return context


class ProfileListView(LoginRequiredMixin, ListView):
  model = Profile
  template_name = 'profiles/profile_list.html'

  def get_queryset(self):
    qs = Profile.objects.get_all_profiles(self.request.user)
    return qs

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    user = User.objects.get(username__iexact=self.request.user)
    profile = Profile.objects.get(user=user)
    rel_r = Relationship.objects.filter(sender=profile)
    rel_s = Relationship.objects.filter(receiver=profile)
    rel_receiver = []
    rel_sender = []
    for item in rel_r:
      rel_receiver.append(item.receiver.user)
    for item in rel_s:
      rel_sender.append(item.sender.user)
    context["rel_receiver"] = rel_receiver
    context["rel_sender"] = rel_sender
    context['is_empty'] = False
    if len(self.get_queryset()) == 0:
      context['is_empty'] = True

    return context


@login_required
def send_invitation(request):
  if request.method == 'POST':
    pk = request.POST.get('profile_pk')
    user = request.user
    sender = Profile.objects.get(user=user)
    receiver = Profile.objects.get(pk=pk)

    rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')
    messages.success(request, f'Friend request sent to {receiver.user}')
    return redirect(request.META.get('HTTP_REFERER'))
  return redirect('profiles:myprofile')


@login_required
def remove_from_friends(request):
  if request.method == 'POST':
    pk = request.POST.get('profile_pk')
    user = request.user
    sender = Profile.objects.get(user=user)
    receiver = Profile.objects.get(pk=pk)

    rel = Relationship.objects.get(
      (Q(sender=sender) & Q(receiver=receiver)) |
      (Q(sender=receiver) & Q(receiver=sender))
    )
    rel.delete()
    messages.info(request, f'{receiver.user} has been removed from your friends list')

    return redirect(request.META.get('HTTP_REFERER'))
  return redirect('profiles:myprofile')
