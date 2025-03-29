from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import date
import json

from core.models import Project, Item, Contact
from core.forms import ProjectForm, ContactForm


@login_required
def project_list(request):
    projects = Project.objects.all()
    today = date.today()

    for project in projects:
        project.task_count = Item.objects.filter(project=project, item_type='task').count()
        project.subproject_count = Item.objects.filter(project=project, item_type='sub_project').count()
        project.activity_count = Item.objects.filter(project=project, item_type='activity').count()
        project.overdue_count = Item.objects.filter(
            project=project,
            due_date__lt=today
        ).exclude(status='completed').count()

    return render(request, 'project/project_list.html', {'projects': projects})


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            messages.success(request, "Project created successfully.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, 'project/project_create.html', {'form': form})


@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'project/project_edit.html', {'form': form, 'project': project})


@login_required
def project_delete(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        confirm_name = request.POST.get('confirm_name', '').strip()
        if confirm_name.lower() == project.name.strip().lower():
            project.delete()
            messages.success(request, "Project deleted successfully.")
            return redirect('project_list')
        else:
            messages.error(request, "Project name does not match. Deletion canceled.")

    return render(request, 'project/project_delete.html', {'project': project})


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    show_closed = request.GET.get('show_closed') == '1'

    def get_filter_param(param):
        return [s.lower() for s in request.GET.getlist(param)]

    task_statuses = get_filter_param("task_status")
    sub_statuses = get_filter_param("sub_status")
    activity_statuses = get_filter_param("activity_status")

    def status_filter(selected):
        if selected:
            return Q(status__in=selected)
        return ~Q(status__in=["completed", "cancelled"]) if not show_closed else Q()

    tasks = Item.objects.filter(project=project, item_type='task').filter(status_filter(task_statuses))
    sub_projects = Item.objects.filter(project=project, item_type='sub_project').filter(status_filter(sub_statuses))
    activities = Item.objects.filter(project=project, item_type='activity').filter(status_filter(activity_statuses))

    for group in [tasks, sub_projects, activities]:
        for item in group:
            if item.updates:
                last = item.updates[-1]
                item.last_update = last.get('timestamp')
                item.last_update_text = last.get('text')
            else:
                item.last_update = None
                item.last_update_text = None

    context = {
        "project": project,
        "tasks": tasks,
        "sub_projects": sub_projects,
        "activities": activities,
        "contacts": Contact.objects.filter(project=project),
        "show_closed": show_closed,
        "task_statuses": task_statuses,
        "sub_statuses": sub_statuses,
        "activity_statuses": activity_statuses,
        "status_options": ["new", "in progress", "completed", "cancelled"],
    }
    return render(request, "project/project_detail.html", context)
