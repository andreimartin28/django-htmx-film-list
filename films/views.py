from typing import Any
from django.db.models.query import QuerySet
from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.contrib.auth import get_user_model
from films.models import Film
from django.views.generic.list import ListView

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods

from films.forms import RegisterForm

# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'
    
class Login(LoginView):
    template_name = 'registration/login.html'


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()  # save the user
        return super().form_valid(form)
    

class FilmList(LoginRequiredMixin, ListView):
    template_name = 'films.html'
    model = Film
    context_object_name = 'films'

    def get_queryset(self):
        user = self.request.user
        return user.films.all()



def check_username(request):
    username = request.POST.get('username')
    if get_user_model().objects.filter(username=username).exists():
        return HttpResponse("<div id='username-error' class='error'>This username already exists</div>")
    else:
        return HttpResponse("<div id='username-error' class='success'>This username is available</div>")

@login_required    
def add_film(request):
    name = request.POST.get('filmname')

    film = Film.objects.create(name=name)

    # add the film to the user's list
    request.user.films.add(film)

    # return template with all of the user's films
    films = request.user.films.all()
    return render(request, 'partials/film-list.html', {'films': films})

@login_required
@require_http_methods(['DELETE'])    
def delete_film(request, pk):
    # remove the film from the user's list
    request.user.films.remove(pk)

    # return the template fragment
    films = request.user.films.all()
    return render(request, 'partials/film-list.html', {'films' : films})
 
 def search_film(request):
    search_text = request.POST.get('search')

    # taxi drive match Taxi Driver
    results = Film.objects.filter(name__icontains=search_text)
    context = {'results': results}
    return render(request, 'partials/search-results.html')