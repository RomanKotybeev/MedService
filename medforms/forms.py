from time import time

from django import forms
from django.urls import reverse

from .models import MedServiceModel


# class MedServiceFormModel(forms.ModelForm):
#     class Meta:
#         model = MedServiceModel
#         fields = ('med_text', 'slug', 'features')
#         widgets = {
#             'med_text': forms.Textarea(attrs={'class': 'materialize-textarea'}),
#             'features': forms.Textarea(attrs={'class': 'materialize-textarea'}),
#         }

from django.utils.text import slugify


# Create your models here.
def gen_slug():
    t = str(int(time()))
    new_slug = slugify(t)
    return new_slug


class MedServiceForm(forms.Form):
    slug = forms.SlugField()
    med_text = forms.Textarea()

    def get_edit_url(self):
        return reverse('edit', kwargs={'slug': self.slug})
