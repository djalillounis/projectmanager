import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from core.models import Project, Task  # Adjust the import paths as needed

def export_tasks_csv(request, project_id):
    """
    Export all tasks for the specified project to a CSV file.
    """
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="project_{project.id}_tasks.csv"'

    writer = csv.writer(response)
    # Write header row
    writer.writerow(['Task ID', 'Task Name', 'Status'])
    # Write task rows
    for task in tasks:
        writer.writerow([task.id, task.name, task.status])

    return response
