from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProjectForm, ItemForm
from .models import Project, Item
from datetime import date
from django.contrib.auth import logout
import json







@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            contacts_data = request.POST.get('contacts_json', '[]')
            try:
                contacts_list = json.loads(contacts_data)
            except json.JSONDecodeError:
                contacts_list = []
            project.contacts = contacts_list
            project.save()
            messages.success(request, "Project updated successfully!")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'project_edit.html', {'form': form, 'project': project})




@login_required
def item_create(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.project = project  # Ensure the item is linked to the project
            item.save()
            messages.success(request, "Item created successfully!")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ItemForm()
    return render(request, 'item_create.html', {'form': form, 'project': project})



@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # Retrieve items for the given project, grouped by type.
    tasks = project.items.filter(item_type='task')
    sub_projects = project.items.filter(item_type='sub_project')
    activities = project.items.filter(item_type='activity')
    context = {
        'project': project,
        'tasks': tasks,
        'sub_projects': sub_projects,
        'activities': activities,
    }
    return render(request, 'project_detail.html', context)










@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    # If Items are related_name='items', you can do:
    items = project.items.all()
    return render(request, 'project_detail.html', {
        'project': project,
        'items': items
    })



@login_required
def project_list(request):
    # Fetch all projects (you can filter by owner if desired)
    projects = Project.objects.all().order_by('-id')
    return render(request, 'project_list.html', {'projects': projects})





@login_required
def custom_logout(request):
    # Accept both GET and POST for logout
    if request.method in ['GET', 'POST']:
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect('login')
    else:
        # If it's neither GET nor POST, reject the request
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['GET', 'POST'])





@login_required
def dashboard(request):
    # Existing counts
    open_items_count = Item.objects.filter(status__in=['new', 'in_progress', 'on_hold']).count()
    high_priority_count = Item.objects.filter(priority='high', status__in=['new','in_progress','on_hold']).count()
    overdue_count = Item.objects.filter(due_date__lt=date.today(), status__in=['new','in_progress','on_hold']).count()
    
    # Build table data for all projects
    projects = Project.objects.all()
    table_data = []
    for project in projects:
        tasks_open = project.items.filter(item_type='task', status__in=['new','in_progress','on_hold']).count()
        subprojects_open = project.items.filter(item_type='sub_project', status__in=['new','in_progress','on_hold']).count()
        activities_open = project.items.filter(item_type='activity', status__in=['new','in_progress','on_hold']).count()
        table_data.append({
            'project': project,
            'tasks_open': tasks_open,
            'subprojects_open': subprojects_open,
            'activities_open': activities_open,
        })

    context = {
        'open_items_count': open_items_count,
        'high_priority_count': high_priority_count,
        'overdue_count': overdue_count,
        'table_data': table_data,  # pass this to the template
    }
    return render(request, 'dashboard.html', context)






@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            # Get the JSON string from the hidden input
            contacts_data = request.POST.get('contacts_json', '[]')
            try:
                contacts_list = json.loads(contacts_data)
            except json.JSONDecodeError:
                contacts_list = []
            # Store it in the project's contacts field
            project.contacts = contacts_list
            project.save()
            messages.success(request, "Project created successfully!")
            return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'project_create.html', {'form': form})
