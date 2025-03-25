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
    # Your original dashboard view logic here...
    pass


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

    return JsonResponse({'success': True})


# Your existing views (item_edit, item_create, project_create, project_edit, etc.) go here
# Make sure to keep them as they are