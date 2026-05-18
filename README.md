# 2026-VK-EDU-Web-11-Petrukhina-A

Учебный Django-проект сайта вопросов и ответов **«Поясняем на котятах»**.

## Страницы

- `/` — новые вопросы
- `/hot/` — популярные вопросы
- `/tag/cats/` — вопросы по тегу
- `/question/1/` — страница вопроса
- `/ask/` — создание вопроса
- `/login/` — вход
- `/signup/` — регистрация
- `/profile/` — профиль

## Запуск локально

Создать виртуальное окружение:

```bash
python -m venv .venv
```

Активировать виртуальное окружение в Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

Запустить сервер:

```bash
python manage.py runserver
```

Открыть сайт:

```text
http://127.0.0.1:8000/
```



## Что сделано
ДЗ2
- Django-приложения `questions` и `core`
- маршруты в `urls.py`
- шаблоны с общим `base.html`
- повторяющиеся блоки через `include`
- пагинация через Django `Paginator`
- статика подключена через `{% static %}`
- ссылки сделаны через `{% url %}`
- добавлены `requirements.txt`, `.gitignore`, `Dockerfile`, `docker-compose.yml`

ДЗ3
- добавлены модели `Profile`, `Tag`, `Question`, `Answer`, `QuestionLike`, `AnswerLike`;
- настроены связи между моделями;
- добавлены ограничения на повторные лайки;
- настроены Model Manager для новых, популярных вопросов и вопросов по тегу;
- настроена админка Django;
- добавлены inline-блоки профиля пользователя и ответов к вопросу;
- добавлена команда `fill_db`;
- страницы вопросов переведены на данные из БД;
- добавлены пустые состояния и обработка 404;
- подключён `django-debug-toolbar`;
- настройки вынесены в `.env`;
- обновлён `docker-compose.yml` с PostgreSQL.
