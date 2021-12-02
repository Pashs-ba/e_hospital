from django.shortcuts import render, redirect
from .forms import PatientForm
from .models import Mutations, Patient
from django.contrib import messages
from ast import literal_eval
from datetime import datetime
from django.db.models import Q
from itertools import zip_longest


def homepage(request):
    context = {'sex_ch': Patient.choices,
               'year': datetime.now().year}

    if request.GET.get('year', None) != 'all' and request.GET.get('year', None):
        context['data'] = Patient.objects.filter(date_of_probe__year=request.GET.get('year')).order_by('name')
        context['selected'] = int(request.GET.get('year'))
    else:
        context['selected'] = 'all'
        context['data'] = Patient.objects.all().order_by('name')
    # print(Patient.objects.all(), Patient.objects.all().order_by('name'))
    print(context['data'])
    years = set()
    for i in Patient.objects.all():
        years.add(i.date_of_probe.year)
    context['years'] = years
    return render(request, 'homepage.html', context)


def new_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            mutation_count = 0
            print(literal_eval(request.POST['mutations']))
            for i in literal_eval(request.POST['mutations']):
                if not Mutations.objects.filter(name=i.upper()):
                    Mutations.objects.create(name=i.upper()).save()
                    mutation_count += 1
                patient.mutations.add(Mutations.objects.get(name=i.upper()))
            patient.save()
            if mutation_count:
                messages.success(request, f'Пациент создан! Создано {mutation_count} мутаций!')
            else:
                messages.success(request, 'Пациент создан!')
        else:
            messages.error(request, 'Ошибка при отправке формы')
        return redirect('homepage')
    else:
        return render(request, 'create_patient.html', {'form': PatientForm()})


def patient_page(request, pk):
    old = Patient.objects.get(pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            old.delete()
            patient = form.save()
            mutation_count = 0
            for i in literal_eval(request.POST['mutations']):
                if not Mutations.objects.filter(name=i.upper()):
                    Mutations.objects.create(name=i.upper()).save()
                    mutation_count += 1
                patient.mutations.add(Mutations.objects.get(name=i.upper()))
            patient.save()
            if mutation_count:
                messages.success(request, f'Пациент обновлен! Создано {mutation_count} мутаций!')
            else:
                messages.success(request, 'Пациент обновлен!')
        return redirect('homepage')
    else:
        form = PatientForm(instance=old, initial={'mutations': list(map(str, old.mutations.all()))})
        return render(request, 'patient_page.html', {'form': form, 'pk': pk})


def delete_patient(request, pk):
    if request.method =='POST':
        Patient.objects.get(pk=pk).delete()
        return redirect('homepage')
    else:
        return render(request, 'delete_page.html')


def queries(request):
    context = {}
    context['sex_ch'] = Patient.choices
    data = Patient.objects.all()
    regions = set()
    years = set()
    context['min_year'] = 10000
    context['max_year'] = 0
    context['max_load'] = 0
    context['min_load'] = 100000000000000000000
    context['max_loyalty'] = 0
    context['min_loyalty'] = 1000
    for i in data:
        context['max_load'] = max(context['max_load'], i.virus_load)
        context['min_load'] = min(context['min_load'], i.virus_load)
        context['max_loyalty'] = max(context['max_loyalty'], i.loyalty)
        context['min_loyalty'] = min(context['min_loyalty'], i.loyalty)
        context['min_year'] = min(datetime.now().year - i.birthday.year, context['min_year'])
        context['max_year'] = max(context['max_year'], datetime.now().year - i.birthday.year)
        regions.add(i.region)
        years.add(i.date_of_probe.year)
    context['regions'] = regions
    context['years'] = years
    if request.GET.get('mutations', None):
        context['s_sex'] = request.GET.get('sex')
        context['s_reg'] = request.GET.getlist('region', None)
        context['s_probe_date'] = list(map(int, request.GET.getlist('probe_date', None)))
        context['s_year_to'] = request.GET.get('year_to')
        context['s_year_from'] = request.GET.get('year_from')
        context['s_load_to'] = request.GET.get('load_to')
        context['s_load_from'] = request.GET.get('load_from')
        context['s_loyalty_to'] = request.GET.get('loyalty_to')
        context['s_loyalty_from'] = request.GET.get('loyalty_from')
        context['s_separator'] = request.GET.get('separate')
        context['s_mean'] = request.GET.get('means')

        sex = Q(patient__sex__in=request.GET.get('sex').split(' '))
        birthday = Q(patient__birthday__year__range=(datetime.now().year - int(request.GET.get('year_to')),
                                                     datetime.now().year - int(request.GET.get('year_from'))))
        region = Q(patient__region__in=request.GET.getlist('region', list(regions)))
        dates = Q(patient__date_of_probe__year__in=list(map(int, request.GET.getlist('probe_date', list(years)))))
        load_range = Q(patient__virus_load__range=[int(request.GET.get('load_from')), int(request.GET.get('load_to'))])
        loyalty_range = Q(
            patient__loyalty__range=[int(request.GET.get('loyalty_from')), int(request.GET.get('loyalty_to'))])

        if request.GET.get('mutations', None) == 'all':
            mutations = Mutations.objects.filter(birthday, sex, region, dates, load_range, loyalty_range)
        else:
            name = Q(name__in=request.GET.get('mutations', None).split(' '))
            mutations = Mutations.objects.filter(name, sex, birthday, region, dates, load_range, loyalty_range)

        context['old_mutations'] = request.GET.get('mutations', '')
        table = []
        match request.GET.get('separate'):
            case 'sex':
                all = []
                for i in request.GET.get('sex').split(' '):
                    if request.GET.get('mutations', None) == 'all':
                        all.append(Mutations.objects.filter(region & birthday & dates & load_range & loyalty_range,
                                                            patient__sex=i).count())
                    else:
                        all.append(Mutations.objects.filter(region & birthday & dates & load_range & loyalty_range,
                                                            patient__sex=i,
                                                            name__in=request.GET.get('mutations', None).split(
                                                                ' ')).count())
                all.append(sum(all))
                for j in set(mutations):
                    tmp = []
                    for i in range(len(request.GET.get('sex').split(' '))):
                        tmp.append(
                            Mutations.objects.filter(region & birthday & dates & load_range & loyalty_range, name=j,
                                                     patient__sex=request.GET.get('sex').split(' ')[i]).count())
                    tmp.append(sum(tmp))
                    if request.GET.get('means') == 'qq':
                        for i in range(len(tmp) - 1):
                            tmp[i] /= all[i]
                    elif request.GET.get('means') == 'all':
                        for i in range(len(tmp) - 1):
                            tmp[i] /= all[-1]
                    table.append(tmp)

                table.append(all)
                context['separator'] = request.GET.get('sex').split(' ')
            case 'age':
                all = []
                for i in range(datetime.now().year - int(request.GET.get('year_to')),
                               datetime.now().year - int(request.GET.get('year_from')) + 1):
                    if Patient.objects.filter(birthday__year=i):
                        if request.GET.get('mutations', None) == 'all':
                            all.append(Mutations.objects.filter(region & sex & dates & load_range & loyalty_range,
                                                                patient__birthday__year=i).count())
                        else:
                            all.append(Mutations.objects.filter(region & sex & dates & load_range & loyalty_range,
                                                                patient__birthday__year=i,
                                                                name__in=request.GET.get('mutations', None).split(
                                                                    ' ')).count())
                all.append(sum(all))
                for j in set(mutations):
                    tmp = []
                    for i in range(datetime.now().year - int(request.GET.get('year_to')),
                                   datetime.now().year - int(request.GET.get('year_from')) + 1):
                        if Patient.objects.filter(birthday__year=i):
                            tmp.append(
                                Mutations.objects.filter(region & sex & dates & load_range & loyalty_range, name=j,
                                                         patient__birthday__year=i).count())
                    tmp.append(sum(tmp))
                    if request.GET.get('means') == 'qq':
                        for i in range(len(tmp) - 1):
                            tmp[i] /= all[i]
                    elif request.GET.get('means') == 'all':
                        for i in range(len(tmp) - 1):
                            tmp[i] /= all[-1]
                    table.append(tmp)

                table.append(all)
                need = []
                for i in range(datetime.now().year - int(request.GET.get('year_to')),
                               datetime.now().year - int(request.GET.get('year_from')) + 1):
                    if Patient.objects.filter(birthday__year=i):
                        need.append(i)
                context['separator'] = need
            case 'region':
                all = []
                for i in request.GET.getlist('region', list(regions)):

                    if request.GET.get('mutations', None) == 'all':
                        all.append(Mutations.objects.filter(birthday & sex & dates & load_range & loyalty_range,
                                                            patient__region=i).count())
                    else:
                        all.append(Mutations.objects.filter(birthday & sex & dates & load_range & loyalty_range,
                                                            patient__region=i,
                                                            name__in=request.GET.get('mutations', None).split(
                                                                ' ')).count())
                all.append(sum(all))
                for j in set(mutations):
                    tmp = []
                    for i in request.GET.getlist('region', list(regions)):
                        tmp.append(
                            Mutations.objects.filter(sex & birthday & dates & load_range & loyalty_range, name=j,
                                                     patient__region=i).count()
                        )
                    tmp.append(sum(tmp))
                    if request.GET.get('means') == 'qq':
                        for i in range(len(tmp) - 1):
                            tmp[i] /= all[i]
                    elif request.GET.get('means') == 'all':
                        for i in range(len(tmp) - 1):
                            tmp[i] /= all[-1]
                    table.append(tmp)
                table.append(all)
                context['separator'] = request.GET.getlist('region', list(regions))
            case 'probe_date':
                all = []

                for i in request.GET.getlist('probe_date', list(years)):
                    if request.GET.get('mutations', None) == 'all':
                        all.append(Mutations.objects.filter(region & sex & birthday & load_range & loyalty_range,
                                                            patient__date_of_probe__year=i).count())
                    else:
                        all.append(Mutations.objects.filter(region & sex & birthday & load_range & loyalty_range,
                                                            patient__date_of_probe__year=i,
                                                            name__in=request.GET.get('mutations', None).split(
                                                                ' ')).count())
                all.append(sum(all))
                for j in set(mutations):
                    tmp = []
                    for i in map(int, request.GET.getlist('probe_date', list(years))):
                        tmp.append(Mutations.objects.filter(sex & birthday & region & load_range & loyalty_range,
                                                            patient__date_of_probe__year=i, name=j).count())
                    tmp.append(sum(tmp))
                    if request.GET.get('means') == 'qq':
                        for i in range(len(tmp) - 1):
                            tmp[i] /= all[i]
                    elif request.GET.get('means') == 'all':
                        for i in range(len(tmp) - 1):
                            tmp[i] /= all[-1]
                    table.append(tmp)
                table.append(all)
                context['separator'] = request.GET.getlist('probe_date', list(years))
        context['mutations'] = list(zip_longest(set(mutations), table, fillvalue='Всего'))
        for_graph = [[] for i in range(len(table[1]) - 1)]
        for i in range(len(table[1]) - 1):
            for j in range(len(table) - 1):
                for_graph[i].append(table[j][i])
        colors = ['rgba(255, 99, 132, 0.5)',
                  'rgba(54, 162, 235, 0.5)',
                  'rgba(255, 206, 86, 0.5)',
                  'rgba(75, 192, 192, 0.5)',
                  'rgba(153, 102, 255, 0.5)',
                  'rgba(255, 159, 64, 0.5)'] * (len(for_graph) // 6+1)
        context['for_graph'] = list(zip(for_graph, colors, context['separator']))
        context['set_mutations'] = set(mutations)

    return render(request, 'queries.html', context)
