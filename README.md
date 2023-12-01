# <img src="https://uralatomprom.ru/static/img/logo.png" width="350" height="120">

Uralatomprom — это веб-приложение для организации работы научной конференции (https://uralatomprom.ru/).

Предусмотрены возможности:
- регистрации участников с закгрузкой тезисов докладов,
- ведения новосного блога для огранизаторов,
- комментирования материалов,
- просмотра профилей пользователей.

### Используемые технологии

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?&style=for-the-badge&logo=mysql&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![GitHub](https://img.shields.io/badge/github%20-%23121011.svg?&style=for-the-badge&logo=github&logoColor=white)

### Необходимые инструменты

* [Python](https://www.python.org/)
* [Pip](https://pypi.org/project/pip/)
* [Django](https://www.djangoproject.com/)
* [MySQL](https://www.mysql.com/)


### Как запустить проект:

* Клонировать репозиторий и перейти в его директорию

* Cоздать и активировать виртуальное окружение:

    * Windows
    ```shell
    python -m venv venv
    ```
    ```shell
    source venv/Scripts/activate
    ```

    * Linux/macOS
    ```shell
    python3 -m venv venv
    ```
    ```shell
    source venv/bin/activate
    ```


* Обновить PIP

    ```shell
    python -m pip install --upgrade pip
    ```

* Установить зависимости из файла requirements.txt:

    ```shell
    pip install -r requirements.txt
    ```

* Выполнить миграции:

    ```shell
    python manage.py makemigrations
    ```
    ```shell
    python manage.py migrate
    ```


* Запустить проект:

    ```shell
    python manage.py runserver
    ```

### Разработка проекта

* Алексей Васильев (aleksey-vasilev) - Бэкэнд, верстка, дизайн, тестирование
