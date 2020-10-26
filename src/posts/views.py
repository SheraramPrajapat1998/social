from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import Post, Like
from profiles.models import Profile
from .forms import PostModelForm, CommentModelForm
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

# search function -> search in profile(fields: first_name, last_name, user)
# posts(fields: contett, author)

def search(request):
  q = request.GET.get('q', None)
  print(q)
  if q is not None:
    all_model_dict = {
      'profiles' : Profile.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(user__username__icontains=q)
      ), 
      'posts': Post.objects.filter(
        Q(content__icontains=q) | Q(author__user__username=q)
      ),
      'q': q,
    }
  else:
    all_model_dict = {}
  print(all_model_dict)
  return render(request, 'search.html', all_model_dict)

@login_required
def myposts(request):
  profile = Profile.objects.get(user=request.user)
  qs = Post.objects.filter(author=profile)
  context = {
    'qs': qs,
    'profile':profile,
  }
  return render(request, 'posts/myposts.html', context)

@login_required
def post_comment_create_and_list_view(request):
  qs = Post.published.all()
  profile = Profile.objects.get(user=request.user)

  # initial data
  p_form = PostModelForm()
  c_form = CommentModelForm()

  profile = Profile.objects.get(user=request.user)

  if 'submit_p_form' in request.POST:
    p_form = PostModelForm(request.POST, request.FILES)
    if p_form.is_valid():
      instance = p_form.save(commit=False)
      instance.author = profile
      messages.success(request, 'Your post has been added.')
      instance.save()
      p_form = PostModelForm()
  
  if 'submit_c_form' in request.POST:
    c_form = CommentModelForm(request.POST)
    if c_form.is_valid():
      instance = c_form.save(commit=False)
      instance.user = profile
      instance.post = Post.objects.get(id=request.POST.get('post_id'))
      messages.success(request, 'Your comment has been added.')
      instance.save()
      c_form = CommentModelForm()
  
  context = {
    'qs': qs,
    'profile': profile,
    'p_form': p_form,
    'c_form': c_form,
  }
  return render(request, 'posts/list.html', context)


@login_required
def like_unlike_post(request):
  user = request.user
  if request.method == 'POST':
    post_id = request.POST.get('post_id')
    post_obj = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)

    if profile in post_obj.liked.all():
      post_obj.liked.remove(profile)
    else:
      post_obj.liked.add(profile)

    like, created = Like.objects.get_or_create(user=profile, post_id=post_id)

    if not created:
      if like.value == 'Like':
        like.value = 'Unlike'
      else:
        like.value = 'Like'
    else:
      like.value = 'Like'

      post_obj.save()
      like.save()
  return redirect('posts:main-post-view')

class PostDeleteView(LoginRequiredMixin, DeleteView):
  model = Post
  template_name = 'posts/confirm_delete.html'
  success_url = reverse_lazy('posts:main-post-view')

  def get_object(self, queryset=None):
    pk = self.kwargs.get('pk')
    obj = Post.objects.get(pk=pk)
    if not obj.author.user == self.request.user:
      messages.warning(self.request, 'You need to be the author of the post in order to delete it.')
    return obj


class PostUpdateView(LoginRequiredMixin, UpdateView):
  form_class = PostModelForm
  model = Post
  template_name = 'posts/update.html'
  success_url = reverse_lazy('posts:main-post-view')

  def form_valid(self, form):
    profile = Profile.objects.get(user=self.request.user)
    if form.instance.author == profile:
      messages.info(self.request, 'Your post has been updated successfully')
      return super().form_valid(form)
    else:

      form.add_error(None, "You need to be the author of the post in order to update it")
      return super().form_invalid(form)