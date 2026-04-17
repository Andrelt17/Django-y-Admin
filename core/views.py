from django.shortcuts import render
from .forms import ContactForm


def home(request):
    form = ContactForm(request.POST or None)
    submitted_data = None
    if request.method == 'POST' and form.is_valid():
        submitted_data = form.cleaned_data
        form = ContactForm()

    return render(request, 'core/form.html', {
        'form': form,
        'submitted_data': submitted_data,
    })
