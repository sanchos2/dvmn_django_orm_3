from random import choice

from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist

from datacenter.models import Chastisement
from datacenter.models import Commendation
from datacenter.models import Lesson
from datacenter.models import Mark
from datacenter.models import Schoolkid


class ScriptError(Exception):
    """Данный класс ошибки реализован исключительно для текущей задачи, дабы не путать Васю умными названиями;)."""

    pass  # noqa: WPS420, WPS604


def get_child(schoolkid):
    """Функция получения ученика из БД."""
    try:
        child = Schoolkid.objects.get(full_name__contains=schoolkid)
    except MultipleObjectsReturned:
        raise ScriptError('Слишком много учеников, уточни параметры запроса!')
    except ObjectDoesNotExist:
        raise ScriptError('В школе нет такого ученика!')
    else:
        return child


def fix_marks(schoolkid):
    """Функция исправляющая оценки."""
    child = get_child(schoolkid)
    marks = Mark.objects.filter(schoolkid=child, points__lt=4)
    for element in marks:
        element.points = 5
        element.save(update_fields=['points'])


def remove_chastisements(schoolkid):
    """Функция удаления жалоб от учителей."""
    child = get_child(schoolkid)
    chastisements = Chastisement.objects.filter(schoolkid=child)
    chastisements.delete()


def create_commendation(schoolkid, title):
    """Функция добавления похвалы от учителей."""
    child = get_child(schoolkid)
    lesson = Lesson.objects.filter(
        group_letter=child.group_letter,
        year_of_study=child.year_of_study,
        subject__title=title,
    ).order_by('-date').first()
    commendation = [
        'Прекрасно!',
        'Ты меня очень обрадовал!',
        'Именно этого я давно ждал от тебя!',
        'Сказано здорово – просто и ясно!',
        'Ты, как всегда, точен!',
        'Очень хороший ответ!',
        'Талантливо!',
        'Ты сегодня прыгнул выше головы!',
        'Я поражен!',
        'Уже существенно лучше!',
        'Потрясающе!',
        'Замечательно!',
        'Прекрасное начало!',
        'Так держать!',
    ]
    if not lesson:
        raise ScriptError('Ошибка в названии предмета')
    Commendation.objects.create(
        text=choice(commendation),  # noqa: S311
        created=lesson.date,
        schoolkid=child,
        subject=lesson.subject,
        teacher=lesson.teacher,
    )
