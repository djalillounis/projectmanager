from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from core.models import Project, Item
from core.forms import ProjectForm, ContactForm


@login_required
def dashboard(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})


@login_required
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            messages.success(request, "Project created successfully!")
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
    tasks = Item.objects.filter(project=project, item_type="task")
    sub_projects = Item.objects.filter(project=project, item_type="sub_project")
    activities = Item.objects.filter(project=project, item_type="activity")
    contacts = project.contacts.all()
    contact_form = ContactForm()
    context = {
        'project': project,
        'tasks': tasks,
        'sub_projects': sub_projects,
        'activities': activities,
        'contacts': contacts,
        'contact_form': contact_form,
    }
    return render(request, 'project_detail.html', context)


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
