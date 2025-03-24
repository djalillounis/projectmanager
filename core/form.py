from django import forms
from .models import Project





class FileUploadForm(forms.Form):
    file = forms.FileField()

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'contacts', 'logo']
