from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from config.choices import EstadoEnvio
from .forms import EncomiendaForm, EstadoCambioForm
from .models import Encomienda


@login_required
def dashboard(request):
    total = Encomienda.objects.count()
    activas = Encomienda.objects.activas().count()
    en_transito = Encomienda.objects.en_transito().count()
    entregadas = Encomienda.objects.entregadas().count()
    retrasadas = Encomienda.objects.con_retraso().count()
    ultimas = Encomienda.objects.order_by('-fecha_registro')[:5]

    return render(request, 'dashboard.html', {
        'total': total,
        'activas': activas,
        'en_transito': en_transito,
        'entregadas': entregadas,
        'retrasadas': retrasadas,
        'ultimas': ultimas,
    })


@login_required
def encomienda_lista(request):
    estado = request.GET.get('estado', '')
    encomiendas_qs = Encomienda.objects.order_by('-fecha_registro')
    if estado in [choice[0] for choice in EstadoEnvio.choices]:
        encomiendas_qs = encomiendas_qs.filter(estado=estado)

    paginator = Paginator(encomiendas_qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'lista.html', {
        'encomiendas': page_obj,
        'estado_seleccionado': estado,
        'estados': EstadoEnvio.choices,
    })


@login_required
def encomienda_detalle(request, pk):
    encomienda = get_object_or_404(Encomienda, pk=pk)
    if request.method == 'POST':
        form = EstadoCambioForm(request.POST, instance=encomienda)
        if form.is_valid():
            nuevo_estado = form.cleaned_data['estado']
            if nuevo_estado != encomienda.estado:
                encomienda.cambiar_estado(nuevo_estado)
                messages.success(request, 'El estado se actualizó correctamente.')
            else:
                messages.info(request, 'No se realizaron cambios en el estado.')
            return redirect('encomienda_detalle', pk=pk)
    else:
        form = EstadoCambioForm(instance=encomienda)

    historial = encomienda.historialestado_set.order_by('-fecha')
    return render(request, 'detalle.html', {
        'encomienda': encomienda,
        'form': form,
        'historial': historial,
    })


@login_required
def encomienda_crear(request):
    if request.method == 'POST':
        form = EncomiendaForm(request.POST)
        if form.is_valid():
            encomienda = form.save()
            messages.success(request, 'Encomienda creada con éxito.')
            return redirect('encomienda_detalle', pk=encomienda.pk)
    else:
        form = EncomiendaForm()

    return render(request, 'form.html', {
        'form': form
    })
