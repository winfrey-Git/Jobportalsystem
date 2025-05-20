from django.shortcuts import render, get_object_or_404
from jobwebsite.models import BlogPost

def blog_list(request):
    posts = BlogPost.objects.all().order_by('-published_date')
    return render(request, 'blog_list.html', {'posts': posts})

def blog_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    return render(request, 'blog_post.html', {'post': post})