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

- Django-приложения `questions` и `core`
- маршруты в `urls.py`
- шаблоны с общим `base.html`
- повторяющиеся блоки через `include`
- пагинация через Django `Paginator`
- статика подключена через `{% static %}`
- ссылки сделаны через `{% url %}`
- добавлены `requirements.txt`, `.gitignore`, `Dockerfile`, `docker-compose.yml`

