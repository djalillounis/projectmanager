from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import date
import json

from .forms import ProjectForm, ItemForm
from .models import Project, Item


@login_required
def item_edit(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            # Check if an update comment or file is provided
            update_comment = request.POST.get('update_comment', '')
            update_file = request.FILES.get('update_file')
            if update_comment or update_file:
                new_update = {'timestamp': timezone.now().isoformat(), 'comment': update_comment}
                if update_file:
                    from django.core.files.storage import default_storage
                    from django.core.files.base import ContentFile
                    file_path = default_storage.save(f'updates/{update_file.name}', ContentFile(update_file.read()))
                    new_update['file'] = file_path
                updates = item.updates if item.updates else []
                updates.append(new_update)
                item.updates = updates
                item.save()
            messages.success(request, "Item updated successfully!")
            return redirect('project_detail', project_id=item.project.id)
    else:
        form = ItemForm(instance=item)
    
    context = {
        'form': form,
        'item': item,
    }
    return render(request, 'item_edit.html', context)






@login_required
def delete_update(request, item_id, timestamp):
    """
    Delete a specific update from an item by matching its timestamp.
    """
    item = get_object_or_404(Item, id=item_id)
    if item.updates:
        # Filter out the update with the matching timestamp
        item.updates = [upd for upd in item.updates if upd.get('timestamp') != timestamp]
        item.save()
        messages.success(request, "Update deleted successfully!")
    return redirect('item_edit', item_id=item_id)

@login_required
def project_edit(request, project_id):
    """
    Edit an existing project, including updating contacts JSON.
    """
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            # Process the contacts JSON
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
    """
    Create a new item under a given project. 
    Optionally preselect item_type via GET parameter (?item_type=task).
    """
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
        form = ItemForm()
        # Optionally preselect the item type if provided in the query
        preselected_type = request.GET.get('item_type')
        if preselected_type in ['task', 'sub_project', 'activity']:
            form.fields['item_type'].initial = preselected_type
    
    return render(request, 'item_create.html', {'form': form, 'project': project})

@login_required
def project_detail(request, project_id):
    """
    Show a project's details, contacts, and items (tasks, sub-projects, activities).
    Supports sorting by ?sort=status or ?sort=priority.
    """
    project = get_object_or_404(Project, id=project_id)
    
    # Retrieve the sort parameter from the GET request
    sort = request.GET.get('sort')
    
    # Base queries for each item type
    tasks_query = project.items.filter(item_type='task')
    sub_projects_query = project.items.filter(item_type='sub_project')
    activities_query = project.items.filter(item_type='activity')
    
    if sort == 'status':
        tasks = tasks_query.order_by('status')
        sub_projects = sub_projects_query.order_by('status')
        activities = activities_query.order_by('status')
    elif sort == 'priority':
        tasks = tasks_query.order_by('priority')
        sub_projects = sub_projects_query.order_by('priority')
        activities = activities_query.order_by('priority')
    else:
        tasks = tasks_query
        sub_projects = sub_projects_query
        activities = activities_query
    
    context = {
        'project': project,
        'tasks': tasks,
        'sub_projects': sub_projects,
        'activities': activities,
    }
    return render(request, 'project_detail.html', context)

@login_required
def project_delete(request, project_id):
    """
    Confirm and delete a project, requiring the user to re-enter the project name.
    """
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation', '')
        if confirmation == project.name:
            project.delete()
            messages.success(request, "Project deleted successfully!")
            return redirect('project_list')
        else:
            messages.error(request, "Project name does not match. Deletion aborted.")
    return render(request, 'project_delete.html', {'project': project})

@login_required
def project_list(request):
    """
    List all projects with basic info, e.g. for a "My Projects" page.
    """
    projects = Project.objects.all().order_by('-id')
    return render(request, 'project_list.html', {'projects': projects})

@login_required
def custom_logout(request):
    """
    Custom logout view that accepts both GET and POST methods.
    """
    if request.method in ['GET', 'POST']:
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect('login')
    else:
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['GET', 'POST'])

@login_required
def dashboard(request):
    """
    Dashboard showing global item counts and a summary of each project's open items.
    """
    open_items_count = Item.objects.filter(status__in=['new', 'in_progress', 'on_hold']).count()
    high_priority_count = Item.objects.filter(priority='high', status__in=['new','in_progress','on_hold']).count()
    overdue_count = Item.objects.filter(due_date__lt=date.today(), status__in=['new','in_progress','on_hold']).count()
    
    projects = Project.objects.all()
    table_data = []
    for proj in projects:
        tasks_open = proj.items.filter(item_type='task', status__in=['new','in_progress','on_hold']).count()
        subprojects_open = proj.items.filter(item_type='sub_project', status__in=['new','in_progress','on_hold']).count()
        activities_open = proj.items.filter(item_type='activity', status__in=['new','in_progress','on_hold']).count()
        table_data.append({
            'project': proj,
            'tasks_open': tasks_open,
            'subprojects_open': subprojects_open,
            'activities_open': activities_open,
        })

    context = {
        'open_items_count': open_items_count,
        'high_priority_count': high_priority_count,
        'overdue_count': overdue_count,
        'table_data': table_data,
    }
    return render(request, 'dashboard.html', context)

@login_required
def project_create(request):
    """
    Create a new project, including a contacts JSON field.
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            contacts_data = request.POST.get('contacts_json', '[]')
            try:
                contacts_list = json.loads(contacts_data)
            except json.JSONDecodeError:
                contacts_list = []
            project.contacts = contacts_list
            project.save()
            messages.success(request, "Project created successfully!")
            return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'project_create.html', {'form': form})

# Additional API endpoint for inline editing of Next Step (if using the code from project_detail)
@require_POST
@login_required
def update_next_step(request, item_id):
    """
    Handle AJAX requests to update an item's next_step_owner field inline.
    """
    item = get_object_or_404(Item, id=item_id)
    try:
        data = json.loads(request.body)
        new_next_step = data.get('next_step', '')
        item.next_step_owner = new_next_step
        item.save()
        return JsonResponse({'next_step': item.next_step_owner})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
