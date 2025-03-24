from django import forms
from .models import Project, Item 

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'logo']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_type', 'short_description', 'due_date', 'status', 'priority', 'owner', 'next_step_owner']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'})
        }
