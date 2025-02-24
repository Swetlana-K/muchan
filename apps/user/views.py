from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.post.models import Post
from .form import RegisterUserForm, ModifyUserForm

# Create your views here.


class UserProfileView(LoginRequiredMixin, View):
    """Show the users profile page if they are logged in."""

    template_name = "user/profile.html"

    def get(self, request):
        posts = (Post.objects
            .select_related("cat_id")
            .prefetch_related("tags")
            .all()
            .filter(user_id = request.user.id)
            .order_by('-created_at')[:10])
        
        context = {
            "posts": posts,
        }
        return render(
            request=request,
            template_name=self.template_name,
            context=context
        )


class UserLogoutView(View):
    """Logout current user session and redirect to the home page"""

    def get(self, request):
        logout(request)
        return redirect("home")


class RegisterUserView(View):
    """Register a new user and redirect to the home page"""
    
    template_name = "user/register.html"
    
    def get(self, request):
        form = RegisterUserForm()
        return render(
            request=request,
            template_name=self.template_name,
            context={'form': form},
        )
        
    def post(self, request):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            return render(
                request=request,
                template_name=self.template_name,
                context={'form': form},
            )
            

class ModifyUserView(View):
    """Modify user details and redirect to the user profile"""
    
    template_name = "user/modify_profile.html"
    
    def get(self, request):
        form = ModifyUserForm(instance=request.user)
        return render(
            request=request,
            template_name=self.template_name,
            context={'form': form},
        )
        
    def post(self, request):
        form = ModifyUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        else:
            return render(
                request=request,
                template_name=self.template_name,
                context={'form': form},
            )