from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProjectForm, ItemForm
from .models import Project, Item
from datetime import date
from django.contrib.auth import logout
import json
from django.utils import timezone


@login_required
def item_edit(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    # Pre-filter updates that include a file
    file_updates = [upd for upd in (item.updates or []) if upd.get('file')]
    
    if request.method == 'POST':
        # Check if this is an update submission (adding an update with file)
        if 'update_form' in request.POST:
            update_comment = request.POST.get('update_comment', '')
            update_file = request.FILES.get('update_file')
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
            messages.success(request, "Update added successfully!")
            return redirect('item_edit', item_id=item.id)
        else:
            form = ItemForm(request.POST, instance=item)
            if form.is_valid():
                form.save()
                messages.success(request, "Item updated successfully!")
                return redirect('project_detail', project_id=item.project.id)
    else:
        form = ItemForm(instance=item)
    context = {
        'form': form,
        'item': item,
        'file_updates': file_updates,
    }
    return render(request, 'item_edit.html', context)



@login_required
def delete_update(request, item_id, timestamp):
    item = get_object_or_404(Item, id=item_id)
    if item.updates:
        # Remove updates with matching timestamp
        item.updates = [upd for upd in item.updates if upd.get('timestamp') != timestamp]
        item.save()
        messages.success(request, "Update deleted successfully!")
    return redirect('item_edit', item_id=item_id)

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
def project_delete(request, project_id):
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
