from ast import If
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .forms import TaskForm
from .models import Task


def home(request):
    return render(request, 'home.html')


def signup(request):

    if request.method == 'GET':
        print('MOSTRAR FORMULARIO GET')
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            # registra usuario
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('task')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'El usuario ya existe'
                })
            except:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'es otro error'
                })

        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Las contraseñas no coinciden'
        })


def view_task(request):
    #tasks = Task.objects.all()
    tasks = Task.objects.filter(usuario=request.user, fechaCompletada__isnull=True)
    return render(request, 'task-crud/visualizar.html', {'tasks': tasks})


def create_task(request):
    if request.method == 'GET':
        return render(request, 'task-crud/añadir.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)#aun no lo guardes 
            new_task.usuario = request.user
            new_task.save()
            return redirect('task')
        except ValueError:
            return render(request, 'task-crud/añadir.html', {
                'form': TaskForm,
                'error': 'Por favor añade datos validos'
            })


def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'el usuario o contraseña es incorrecto'
            })
        else:
            login(request, user)
            return redirect('task')
