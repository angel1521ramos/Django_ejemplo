from ast import If
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required


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

@login_required
def view_task(request):
    #tasks = Task.objects.all()
    tasks = Task.objects.filter(
        usuario=request.user, fechaCompletada__isnull=True)
    return render(request, 'task-crud/visualizar.html', {'tasks': tasks})

@login_required
def view_task_completed(request):
    tasks = Task.objects.filter(
        usuario=request.user, fechaCompletada__isnull=False).order_by('-fechaCompletada')
    return render(request, 'task-crud/visualizar.html', {'tasks': tasks})

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'task-crud/añadir.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)  # aun no lo guardes
            new_task.usuario = request.user
            new_task.save()
            return redirect('task')
        except ValueError:
            return render(request, 'task-crud/añadir.html', {
                'form': TaskForm,
                'error': 'Por favor añade datos validos'
            })

@login_required
def detail_task(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, usuario=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task-crud/detalle.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, usuario=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('task')
        except ValueError:
            return render(request, 'task-crud/detalle.html', {'task': task, 'form': form, 'error': "error actualizando la tarea"})

@login_required
def completed_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, usuario=request.user)
    if request.method == 'POST':
        task.fechaCompletada = timezone.now()
        task.save()
        return redirect('task')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, usuario=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task')

@login_required
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
