from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import date
import json

from .forms import ProjectForm, ItemForm, ContactForm
from .models import Project, Item, Contact


@login_required
def dashboard(request):
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
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {'projects': projects})


@login_required
def item_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.project = project
            item.save()
            messages.success(request, "Item created successfully!")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ItemForm(initial={'item_type': request.GET.get('item_type')})
    return render(request, 'item_create.html', {'form': form, 'project': project})


@login_required
def item_edit(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated successfully!")
            return redirect('project_detail', project_id=item.project.id)
    else:
        form = ItemForm(instance=item)
    return render(request, 'item_edit.html', {'form': form, 'item': item})


@require_POST
@login_required
def update_next_step(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    data = json.loads(request.body)
    item.next_step_owner = data.get('next_step_owner')
    item.save()
    return JsonResponse({'success': True})


# ✅ NEW VIEWS BELOW

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
def add_contact(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    form = ContactForm(request.POST)
    if form.is_valid():
        contact = form.save(commit=False)
        contact.project = project
        contact.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})


@require_POST
@login_required
def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    contact.delete()
    return JsonResponse({'success': True})


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
