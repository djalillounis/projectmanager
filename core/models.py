from django.db import models










class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    contacts = models.JSONField(null=True, blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    def __str__(self):
        return self.name

class Item(models.Model):
    ITEM_TYPES = [
        ('task', 'Task'),
        ('sub_project', 'Sub-Project'),
        ('activity', 'Activity'),
    ]
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    short_description = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    owner = models.CharField(max_length=100)
    next_step_owner = models.CharField(max_length=100, blank=True)
    updates = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.item_type}: {self.short_description}"

