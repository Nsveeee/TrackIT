from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db.models import Q
from .models import Bug, Project, Comment, User


def _redirect_for_role(role: str):
    return 'admin_dashboard' if role == 'ADMIN' else 'dashboard'


def _require_admin(user):
    return getattr(user, 'role', None) == 'ADMIN'


def login_view(request):
    if request.method == "POST":
        selected_role = request.POST.get('role')
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            if selected_role and getattr(user, 'role', None) != selected_role:
                # Role selected doesn't match the user's actual role.
                return render(request, 'login.html', {'error': 'Invalid role selection.'})
            login(request, user)
            return redirect(_redirect_for_role(getattr(user, 'role', None)))
    return render(request, 'login.html')


@login_required
def dashboard(request):
    # Common dashboard for DEV/REPORTER (admin has its own).
    if _require_admin(request.user):
        return redirect('admin_dashboard')

    bugs = Bug.objects.prefetch_related('comment_set__user').all()
    
    counts = {
        'open': bugs.filter(status='OPEN').count(),
        'in_progress': bugs.filter(status='IN_PROGRESS').count(),
        'resolved': bugs.filter(status='RESOLVED').count(),
        'closed': bugs.filter(status='CLOSED').count(),
    }

    search_query = request.GET.get('q')
    if search_query:
        bugs = bugs.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        
    projects = Project.objects.all()
    return render(request, 'dashboard.html', {'bugs': bugs, 'counts': counts, 'projects': projects})


@login_required
def admin_dashboard(request):
    if not _require_admin(request.user):
        return HttpResponseForbidden("Admins only.")

    bugs = Bug.objects.prefetch_related('comment_set__user').all()
    
    counts = {
        'open': bugs.filter(status='OPEN').count(),
        'in_progress': bugs.filter(status='IN_PROGRESS').count(),
        'resolved': bugs.filter(status='RESOLVED').count(),
        'closed': bugs.filter(status='CLOSED').count(),
    }

    search_query = request.GET.get('q')
    if search_query:
        bugs = bugs.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        
    projects = Project.objects.all()
    developers = User.objects.filter(role='DEV')
    return render(
        request,
        'admin_dashboard.html',
        {'bugs': bugs, 'counts': counts, 'developers': developers, 'projects': projects},
    )


@login_required
def report_bug(request):
    projects = Project.objects.all()
    if request.method == "POST":
        Bug.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            priority=request.POST['priority'],
            project_id=request.POST['project'],
            reporter=request.user
        )
        return redirect(_redirect_for_role(getattr(request.user, 'role', None)))
    return render(request, 'report.html', {'projects': projects})


@login_required
def update_status(request, id):
    if getattr(request.user, 'role', None) != 'DEV':
        return HttpResponseForbidden("Only developers can update bug status.")

    bug = get_object_or_404(Bug, id=id)
    bug.status = request.POST['status']
    bug.save()
    return redirect(_redirect_for_role(getattr(request.user, 'role', None)))


@login_required
def add_comment(request, id):
    bug = get_object_or_404(Bug, id=id)
    Comment.objects.create(
        bug=bug,
        user=request.user,
        text=request.POST['text']
    )
    return redirect(_redirect_for_role(getattr(request.user, 'role', None)))


@login_required
def admin_assign_bug(request, id):
    if not _require_admin(request.user):
        return HttpResponseForbidden("Admins only.")

    bug = get_object_or_404(Bug, id=id)
    developer_id = request.POST.get('assigned_to')
    if developer_id:
        bug.assigned_to_id = int(developer_id)
        bug.save()
    return redirect('admin_dashboard')


@login_required
def admin_delete_bug(request, id):
    if not _require_admin(request.user):
        return HttpResponseForbidden("Admins only.")

    bug = get_object_or_404(Bug, id=id)
    bug.delete()
    return redirect('admin_dashboard')


@login_required
def admin_update_project_devs(request, id):
    if not _require_admin(request.user):
        return HttpResponseForbidden("Admins only.")

    project = get_object_or_404(Project, id=id)
    dev_ids = request.POST.getlist("developers")
    devs = User.objects.filter(role="DEV", id__in=dev_ids)
    project.developers.set(devs)
    messages.success(request, f"Developers updated for project '{project.name}'.")
    return redirect("admin_dashboard")


@login_required
def admin_create_project(request):
    if not _require_admin(request.user):
        return HttpResponseForbidden("Admins only.")

    if request.method == "POST":
        project = Project.objects.create(
            name=request.POST['name'],
            description=request.POST['description'],
        )
        messages.success(request, f"Project '{project.name}' created successfully.")
    return redirect('admin_dashboard')


@login_required
def admin_edit_project(request, id):
    if not _require_admin(request.user):
        return HttpResponseForbidden("Admins only.")

    project = get_object_or_404(Project, id=id)
    if request.method == "POST":
        project.name = request.POST['name']
        project.description = request.POST['description']
        project.save()
        
        dev_ids = request.POST.getlist("developers")
        devs = User.objects.filter(role="DEV", id__in=dev_ids)
        project.developers.set(devs)
        
        messages.success(request, f"Project '{project.name}' successfully updated.")
    return redirect('admin_dashboard')


@login_required
def admin_delete_project(request, id):
    if not _require_admin(request.user):
        return HttpResponseForbidden("Admins only.")

    project = get_object_or_404(Project, id=id)
    project_name = project.name
    project.delete()
    messages.success(request, f"Project '{project_name}' deleted.")
    return redirect('admin_dashboard')