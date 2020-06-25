from time import time
from django.contrib import messages
from django.contrib.messages import get_messages
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.utils.text import slugify
from django.views import View
from .models import MedServiceModel
from .forms import MedServiceForm
from .parsing.parsing import txt_or_img, read_comments
from .parsing.extract_module import extract
import json
from django.core.serializers.json import DjangoJSONEncoder


def gen_slug():
    t = str(int(time()))
    new_slug = slugify(t)
    return new_slug


class Home(View):
    # form = MedServiceForm
    template_name = 'medforms/index.html'

    def get(self, request):
        return render(
            request,
            self.template_name,
        )

    def post(self, request):
        slug = gen_slug()
        uploaded_files = request.FILES['documents']
        med_text = txt_or_img(uploaded_files)
        request.session['med_text'] = med_text
        return redirect(reverse('edit', args=[slug]))


class UpdateMedService(View):
    # model = MedServiceModel
    # form = MedServiceForm
    template_name = 'medforms/edit.html'

    def get(self, request, slug):
        med_text = request.session['med_text']
        return render(
            request,
            self.template_name,
            {'med_text': med_text, 'slug': slug}
        )

    def post(self, request, slug):
        request.session['med_text'] = request.POST.get('textarea_name')
        features = extract(request.session['med_text'])[0]
        feat_indices = extract(request.session['med_text'])[1]
        return render(
            request,
            self.template_name,
            {
                'med_text': request.session['med_text'],
                'slug': slug,
                'features': features,
                'feat_indices': feat_indices,
            }
        )
