from django.db import models


class Mutations(models.Model):
    name = models.CharField(max_length=1024)

    def __str__(self):
        return self.name


class Patient(models.Model):
    choices = {0: 'М', 1: 'Ж'}
    name = models.CharField(verbose_name='Имя', max_length=1024)
    sex = models.IntegerField(choices=[(0, 'М'), (1, 'Ж')], verbose_name="Пол")
    birthday = models.DateField(auto_now=False, verbose_name="Дата Рождения", null=True)

    region = models.CharField(verbose_name='Регион', max_length=1024)
    date_of_probe = models.DateField(auto_now=False, verbose_name="Дата забора")
    virus_load = models.IntegerField(verbose_name='Вирусная нагрузка', blank=True, null=True)
    loyalty = models.IntegerField(verbose_name="Приверженность*", blank=True, null=True, max_length=1024, default=100)

    mutations = models.ManyToManyField(Mutations, null=True)

    class Meta:
        verbose_name = 'Пациент'
        verbose_name_plural = 'Пациенты'

    def __str__(self):
        return f'{self.name} {self.date_of_probe}'

