from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from core.models import Project, Item, Contact
from core.forms import ProjectForm, ContactForm
from datetime import date
from django.db.models import Q

@login_required
def dashboard(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})


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

    return render(request, 'project_list.html', {'projects': projects})


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()

            # Handle contacts JSON
            contacts_json = request.POST.get('contacts_json', '[]')
            try:
                contacts_data = json.loads(contacts_json)
                for contact in contacts_data:
                    name = contact.get('name', '').strip()
                    email = contact.get('email', '').strip()
                    phone = contact.get('phone', '').strip()
                    role = contact.get('role', '').strip()
                    if name or email or phone or role:
                        Contact.objects.create(
                            project=project,
                            name=name,
                            email=email,
                            phone=phone,
                            role=role,
                            contact_type='external'
                        )
            except json.JSONDecodeError:
                messages.warning(request, "Some contacts could not be processed.")

            messages.success(request, "Project and contacts created successfully!")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, 'project_create.html', {'form': form})


@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully!")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'project_edit.html', {'form': form, 'project': project})


@login_required
def project_delete(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        confirm_name = request.POST.get('confirm_name')
        if confirm_name == project.name:
            project.delete()
            messages.success(request, "Project deleted successfully.")
            return redirect('project_list')
        else:
            messages.error(request, "Project name does not match. Deletion canceled.")
    return render(request, 'project_delete.html', {'project': project})



@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    selected_statuses = [s.lower() for s in request.GET.getlist('status')]
    show_closed = request.GET.get('show_closed') == '1'

    # Normalize possible statuses (update these to match DB values)
    status_options = ['new', 'in progress', 'completed', 'cancelled']

    if selected_statuses:
        status_filter = Q(status__in=selected_statuses)
    elif show_closed:
        status_filter = Q()  # All statuses
    else:
        status_filter = ~Q(status__in=["completed", "cancelled"])

    tasks = Item.objects.filter(project=project, item_type='task').filter(status_filter)
    sub_projects = Item.objects.filter(project=project, item_type='sub_project').filter(status_filter)
    activities = Item.objects.filter(project=project, item_type='activity').filter(status_filter)

    context = {
        "project": project,
        "tasks": tasks,
        "sub_projects": sub_projects,
        "activities": activities,
        "show_closed": show_closed,
        "selected_statuses": selected_statuses,
        "status_options": status_options,
    }
    return render(request, "project_detail.html", context)








@require_POST
@login_required
def update_project_info(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    data = json.loads(request.body)
    name = data.get("name", "").strip()
    description = data.get("description", "").strip()

    if name:
        project.name = name
    project.description = description
    project.save()

    return JsonResponse({'success': True, 'name': project.name})
