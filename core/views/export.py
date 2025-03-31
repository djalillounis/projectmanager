import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from ..models import Project, Item

def export_tasks_csv(request, project_id):
    """
    Export all tasks for the specified project (where item_type is 'task') to a CSV file.
    """
    project = get_object_or_404(Project, id=project_id)
    tasks = Item.objects.filter(project=project, item_type='task')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="project_{project.id}_tasks.csv"'

    writer = csv.writer(response)
    # Write CSV header
    writer.writerow(['Task ID', 'Short Description', 'Status'])
    
    # Write each task row
    for task in tasks:
        writer.writerow([task.id, task.short_description, task.status])
    
    return response
