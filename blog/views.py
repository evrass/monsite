from django.core.paginator import EmptyPage , PageNotAnInteger, Paginator 
from django.shortcuts import get_object_or_404,  render 
from .models import Post 
from django.views.generic import ListView 
from .forms import EmailPostForm 
from django.core.mail import send_mail 

class PostListView(ListView): 
 
     """ 
     Alternative post list view 
     """ 
     queryset = Post.published.all() 
     context_object_name = 'posts' 
     paginate_by = 3 
     template_name = 'blog/post/list.html' 


def post_list(request): 
    post_list = Post.published.all() 

    #Pagination avec 3 articles par page
    paginator = Paginator(post_list, 3) 
    
    page_number = request.GET.get('page') 
    try: 
         posts = paginator.page(page_number)

    except PageNotAnInteger: 
        # Si page_number n'est pas un entier, récupérez la première page
         posts = paginator.page(1) 
    except EmptyPage: 

        #Si page_number est hors de portée, obtenez la dernière page de résultats 
         posts = paginator.page(paginator.num_pages) 

    return render( 
         request, 
      'blog/post/list.html', 
      {'posts': posts} 
   ) 

#Créons une deuxième vue pour afficher un seul article
def post_detail(request, year, month, day, post): 
    post = get_object_or_404( 
        Post, 
        status=Post.Status.PUBLISHED,
        slug=post, 
        publish__year=year, 
        publish__month=month, 
        publish__day=day) 
   
    return render( 
        request, 
        'blog/post/detail.html', 
        {'post': post} 
 ) 


# Nous allons creer une vue pour gerer le formulaire d'envoi par email
def post_share(request, post_id): 
    
    # Récupérer la publication par identifiant
    post = get_object_or_404( 
    
         Post, 
         id=post_id, 
         status=Post.Status.PUBLISHED 
 
    ) 

    sent=False
    if request.method == 'POST': 
        #Le formulaire a été soumis
        form = EmailPostForm(request.POST) 
        if form.is_valid(): 

             # Les champs du formulaire ont été validés
             cd = form.cleaned_data 
             
             post_url = request.build_absolute_uri( 
                 post.get_absolute_url() 
             ) 
             subject = ( 
                 f"{cd['name']} ({cd['email']}) " 
                 f"recommends you read {post.title}" 
             ) 
             message = ( 
                 f"Read {post.title} at {post_url}\n\n" 
                 f"{cd['name']}\'s comments: {cd['comments']}" 
            ) 
             send_mail( 
                 subject=subject, 
                 message=message, 
                 from_email=None, 
                 recipient_list=[cd['to']] 
            ) 
             sent = True 

    else: 
        form = EmailPostForm() 
    return render( 
request, 
    'blog/post/share.html', 
      { 
    
        'post': post, 
        'form': form, 
        'sent': sent 

      } 
) 