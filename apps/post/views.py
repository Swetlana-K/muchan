from typing import Optional
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.user.models import User
from .models import Post, Comment, PostTag, Category, Tag
from .form import NewComment, NewPost


# Create your views here.

class HomePageView(View):
    """Home Page with the 10 most recent posts displayed
    """
    template_name = "index.html"
    
    def get(self, request):
        posts = (Post.objects
            .select_related("user_id", "cat_id")
            .prefetch_related("tags")
            .all()
            .order_by('-created_at')[:10])

        form = AuthenticationForm()
        
        context = {
            "posts": posts,
            "form": form
        }
        return render(
            request=request, 
            template_name=self.template_name, 
            context=context
        )
        
    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # extract username and password
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # authenticate the user
            user: Optional[User] = authenticate(
                username = username,
                password = password)
            # check if user was successfully authenticated
            if user is not None:
                # use the session to keep the authenticated users's id
                login(request, user)
                
                # Redirect the user to his profile page
                return redirect('profile')
            else:
                # TODO: what should happen if the user is not authenticated?
                pass
        else:
            self.error_message = "Sorry, something went wrong. Try again."
            
            return render(
            request=request,
            template_name=self.template_name,
            context={'form': form, 'error_message': self.error_message},
            )

class PostPageView(LoginRequiredMixin, View):
    """Display the detailed page of a specific post.
    
    Offers the possibility to post a comment for that post.
    """

    template_name = "post/post.html"

    def get(self, request, post_id):

        self.post_data = (Post.objects
                .select_related("user_id", "cat_id")
                .prefetch_related("tags")
                .get(pk=post_id))
        self.comments = (Comment.objects
                    .select_related("user_id")
                    .all()
                    .filter(post_id = post_id)
                    .order_by('-created_at'))

        self.context = {
            "title": self.post_data.title,
            "username": self.post_data.user_id.username,
            "image": self.post_data.image.url,
            "upvotes": self.post_data.userUpVotes.count(),
            "downvotes": self.post_data.userDownVotes.count(),
            "category": self.post_data.cat_id.cat,
            "tags": ", ".join([tag.name for tag in self.post_data.tags.all()]),
            "comments": self.comments
        }
        form = NewComment()
        self.context["form"] = form
        return render(
            request=request, 
            template_name=self.template_name, 
            context=self.context
        )
        
    def post(self, request, post_id):
        form = NewComment(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            new_comment = Comment.objects.create(
                user_id = request.user,
                post_id = Post.objects.get(pk=post_id),
                body = data["body"]
            )
            return redirect('post-detail', post_id)
        return render(
            request=request, 
            template_name=self.template_name, 
            context=self.context
        )
        

class NewPostView(LoginRequiredMixin, View):
    """Display the page to create a new post.
    On successful creation, redirects to the detail page for that post.
    """
    template_name = "post/new_post.html"
    
    def get(self, request):
        form = NewPost()
        return render(
            request=request,
            template_name=self.template_name,
            context={'form': form},
        )
    
    def post(self, request):
        form = NewPost(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            created_post = Post.objects.create(
                user_id=request.user, 
                title=data['title'], 
                image=data.get('image'),
                cat_id=Category.objects.get(pk=data['cat_id'])
            )
            created_post.save()
            for tag in data["tags"]:
                PostTag.objects.create(
                    post_id=created_post, 
                    tag_id=Tag.objects.get(pk=tag)
                )
            return redirect('post-detail', created_post.id)
        return render(
            request=request,
            template_name=self.template_name,
            context={'form': form},
        )