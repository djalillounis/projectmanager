from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    ##  contacts = models.JSONField(null=True, blank=True)  old contacts field
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
    next_step = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.item_type}: {self.short_description}"
    



class Contact(models.Model):
    CONTACT_TYPE_CHOICES = [
        ('internal', 'Internal'),
        ('external', 'External'),
    ]

    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPE_CHOICES, default='external')

    def __str__(self):
        return f"{self.name} ({self.contact_type})"
0