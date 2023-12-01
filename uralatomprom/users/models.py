from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from blog.constants import MAX_LENGTH


class Participant(AbstractUser):

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        help_text=('Обязательное поле. Не более 150 символов. '
                   'Только буквы и цифры'),
        validators=[RegexValidator(r'^[a-zA-Z0-9]*$',
                                   'Только латинские буквы и цифры')],
        error_messages={
            'unique': 'Пользователь с таким именем уже есть',
        }
    )

    is_speaker = models.BooleanField('С докладом', null=True)
    full_name = models.CharField('ФИО (полностью)',
                                 max_length=MAX_LENGTH,
                                 null=True)
    organisation = models.CharField('Название организации',
                                    max_length=MAX_LENGTH,
                                    null=True, blank=True)
    phone = models.CharField('Телефон участника',
                             max_length=MAX_LENGTH,
                             null=True, blank=True)
    abstract = models.FileField('Тезисы доклада',
                                upload_to='abstracts',
                                blank=True,
                                help_text=u'<a href="/abstracts/template.doc"'
                                '>Шаблон тезисов доклада</a> Название файла'
                                ' должно быть в виде "IvanovAV.doc". Тезисы'
                                ' можно загрузить позднее через форму'
                                ' редактирования профиля участника.')
    email = models.EmailField('E-mail: ', null=True)
    give_personal_data = models.BooleanField(
        'Согласие на обработку персональных данных',
        help_text=u'Я прочитал и принимаю <a href="/abstracts/personal.doc'
        '">условия обработки персональных данных.</a>',
        default=True
        )

    def __str__(self):
        return self.username
