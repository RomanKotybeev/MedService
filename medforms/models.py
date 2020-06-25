from django.db import models
from time import time

from django.urls import reverse
from django.utils.text import slugify


# Create your models here.
def gen_slug():
    t = str(int(time()))
    new_slug = slugify(t)
    return new_slug


class MedServiceModel(models.Model):
    med_text = models.TextField()
    features = models.TextField(blank=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        self.slug = gen_slug()
        super().save(*args, **kwargs)

    def get_edit_url(self):
        return reverse('edit', kwargs={'slug': self.slug})
