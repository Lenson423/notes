# Notes

## Содержание

### [Backend](#backend)

### [Frontend](#frontend)

# Backend

## Docker

Этот проект использует Docker Compose для создания и управления контейнерами для backend, frontend и Redis.

### Шаги по запуску:

1. **Убедитесь, что у вас установлены Docker и Docker Compose.**
   Для установки Docker и Docker Compose следуйте официальным инструкциям:
    - [Установка Docker](https://docs.docker.com/get-docker/)
    - [Установка Docker Compose](https://docs.docker.com/compose/install/)

2. **Перейдите в директорию проекта.**
   Если проект еще не клонирован, выполните команду:
   ```bash
   git clone https://github.com/Lenson423/notes
   cd <папка_проекта>

3. **В корневой директории проекта выполните команду**:

```bash
docker-compose up --build
```

4. **Откройте приложение в браузере.**
   После успешного запуска откройте в браузере: http://localhost:8000

5.**Остановка контейнеров.**
Для остановки контейнеров выполните команду:

```bash
docker-compose down
```

## Описание проекта

<p>Notes — это гибкая платформа для создания,организации и управления информацией, объединяющая функции заметок, 
баз данных и планирования. Пользователи смогут создавать страницы с текстом, таблицами, списками задач, встроенными
медиа. Основная идея — предоставить универсальный инструмент для работы и личного использования, который позволит
пользователям легко организовывать свои проекты, задачи, цели и заметки в одном месте.</p>

## Стек используемых технологий

<h4>Фреймворки и библиотеки для веб-разработки:</h4>
<ul>
<li>Django (4.2)
<li>djangorestframework (3.15.2)
<li>django-crispy-forms (2.3)
<li>django-taggit (6.0.0)
<li>Django Summernote (0.8.20.0)
<li>djangorestframework-simplejwt (4.5.0)
</ul> 
<h4>Для работы с JSON, API и веб-запросами:</h4>
<ul>
<li>jsonschema (4.23.0)
<li>requests (2.32.3)
<li>httpcore (1.0.5)
<li>urllib3 (2.2.2)
<li>fastjsonschema (2.20.0)
</ul>
<h4>Для обработки документов и работы с PDF:</h4>
<ul>
<li>reportlab (4.0.9)
<li>xhtml2pdf (0.2.16)
<li>pypdf (5.0.0)
<li>PyPDF2 (1.26.0)
</ul>
<h4>Для работы с SQL и базами данных:</h4>
<ul>
<li>sqlparse (0.5.1)
<li>oscrypto (1.3.0)
</ul>

## Роли пользователя

<img src="UML/Варианты_использования.drawio.png" alt="Тут должны быть роли пользователя">

### Владелец

##### Пользователь с полными правами на управление системой, который может настраивать параметры, управлять пользователями и разрабатывать новые функции.

К его функционалу относятся:
<ul>
<li> Функционал всех остальных групп
<li> Назначение Администраторов (path('admin/', admin.site.urls))
</ul>

### Администратор

##### Пользователь, ответственный за управление учетными записями, поддержку пользователей и настройку безопасности системы.

К его функционалу относятся:
<ul>
<li> Функционал Пользователя
<li> Динамическое управление правами Пользователя и Гостя (path('admin/', admin.site.urls))
</ul>

### Пользователь

##### Пользователь с полным доступом к системе. Может входить в учётную запись. Может создавать, редактирвать и удалять страницы. Может создавать заметки, таблицы, календари, комментарии на страницах. Может добавлять изображения на страницы. Может делиться странцицами.

К его функционалу относятся:
<ul>
<li> Все действия, касающиеся работы с заметками
<ul>
    <li>path('notes/', login_required(views.home), name='notes') </li>
    <li>path('notes/search/', views.search_note, name='search_note')</li>
    <li>path('notes/<slug:slug>/', login_required(views.get_note_details), name='note_detail')</li>
    <li>path('notes/<int:pk>/delete/', login_required(views.delete_note), name='delete_single_note')</li>
    <li>path('notes/<int:pk>/delete/confirm/', login_required(views.confirm_delete_note), name='confirm_delete_note')</li>
    <li>path('notes/<int:pk>/edit/', login_required(views.edit_note_details), name='note_details_edit')</li>
    <li>path('notes/<slug:slug>/pdf/', login_required(views.generate_pdf), name='note_as_pdf')</li>
    <li>path('notes/share/<str:signed_pk>/', views.get_shareable_link, name='share_notes')</li>
    <li>path('tags/<slug:slug>/', views.get_all_notes_tags, name='get_all_notes_tags')</li>
    <li>path('', views.home, name='home')
</ul>
<li> Работа с аккаунтом (смена пароля и т.п.)
<ul>
<li>path('accounts/logout/', views.View.logout_view, name='logout')</li>
<li>path('accounts/change_password/', views.View.change_password, name='change_password')</li>
</ul>
<li> Все права гостя 
</ul>

### Гость

##### Пользователь с ограниченным доступом к системе. Может просматривать общедоступные страницы, но не может вносить изменения. Может подать запрос на создание учётной записи (зарегестрироваться)

К его функционалу относится:

<ul>
<li>Работа с чатом (path('<str:room_name>/', views.room, name='rooms'))</li>
<li>Создание аккаунта и вход в него
<ul>
<li>path('accounts/signup/', views.View.signup, name='signup')</li>
<li>path('accounts/login/', LoginView.as_view(redirect_authenticated_user=True), name='login')</li>
</ul>
</li>

</ul>

<p>Система создания, организации и управления информацией. Владелец системы управляет учётными записями пользователей, которые предоставляются после регистрации и данными, привязанными к ним, и управляет параметрами системы и создаёт функции, которые влияют на опыт использования системы. Также владелец создает страницу для записи пользователем информации и предоставляет пользователю доступ на редактирование. Администратор системы управляет настройками безопасности, обеспечивает поддержку пользователей и решает технические вопросы. Гость системы может послать администратору запрос на заведение учётной записи, в этом случае происходит автоматическое создание новой учётной записи, которая требует подтверждения от владельца, после которого такая учётная запись будет доступна для использования. Также гость может просматривать страницы других пользователей и войти в существующую учётную запись. Пользователь системы может редактировать созданные страницы, добавлять таблицы, списки задач, календари, комментарии, изображения на страницы. Также пользователь может послать администратору запрос на изменение пароля с деталями о новом пароле, в этом случае происходит автоматическая генерация нового пароля, которая требует от владельца подтверждения, после которого такой пароль будет использоваться для получения пользователем доступа к учётной записи. Также пользователь может поделиться страницей.</p>

## База данных

<p> Для использования была выбрана база данных MySQL, как наиболее простая для использования,
и, самое главное, хорошо совместимая со всеми библиотеками</p>

<img src="notes/sql/DB_image.png" alt="Схема базы данных">
<img src="notes/sql/ER-diagram.png" alt="ER-диаграмма">

## API маршруты

<h4>Аутентификация</h4>
<ul>
<li>POST /api/token/ – Получение JWT токена.
<li>POST /api/token/refresh/ – Обновление JWT токена.
</ul>

<h4>Пользовательские действия</h4>
<ul>
<li>GET /accounts/signup/ – Страница регистрации пользователя.
<li>GET /accounts/login/ – Страница входа (редирект если пользователь уже аутентифицирован).
<li>GET /accounts/logout/ – Выход из аккаунта.
<li>GET /accounts/change_password/ – Изменение пароля.
</ul>

<h4>Работа с заметками</h4>
<ul>
    <li>GET /notes/ – Домашняя страница с заметками (требуется авторизация).</li>
    <li>GET / – Домашняя страница.</li>
    <li>GET /notes/search/ – Поиск заметок (требуется авторизация).</li>
    <li>GET /notes/<slug:slug>/ – Детали заметки (требуется авторизация).</li>
    <li>GET /notes/<int:pk>/delete/ – Удаление заметки (требуется авторизация).</li>
    <li>GET /notes/<int:pk>/delete/confirm/ – Подтверждения удаления заметки (требуется авторизация).</li>
    <li>GET /notes/<int:pk>/edit/ – Редактирование заметки (требуется авторизация).</li>
    <li>GET /notes/<slug:slug>/pdf/ – Генерация PDF-версии заметки (требуется авторизация).</li>
    <li>GET /notes/share/<str:signed_pk>/ – Получение ссылки для просмотра заметки.</li>
</ul>

<img src="src/readmeIMG0.png" alt="Swagger UI">

<h4>Организация сетевого взаимодействия</h4>
<p>Сервер в данный момент доступен через hamachi. Для подключения необходимо подключиться к существующей сети LensonNet. Сам сервер будет доступен по адресу http://25.31.176.32:8000 (как в hamachi организовать https еще не догадались :))</p>
<p>График работы сервера - в разработке. Ответственный - https://t.me/DancingWithTheSunRays</p>

# Frontend

## Описание проекта

### [Описание проекта можно прочесть выше](#описание-проекта)

## Стек используемых технологий

<ul>
<li>Figma – Используется для проектирования интерфейсов, прототипирования и создания макетов пользовательского интерфейса (UI).
<li>Bootstrap – Фреймворк для быстрой и адаптивной верстки, используемый для реализации интерфейса на фронтенде.
</ul>

## Прототипы страниц

### [Десктопный дизайн](https://www.figma.com/design/nfZD6QHBtFL7f2xXTvDdAw/Comp)

### [Мобильный дизайн](https://www.figma.com/design/tRNl6nzTKKYvTG7Kk6PSpr/mobile)

### [Планшетный дизайн](https://www.figma.com/design/NLEtUPq2fvkz7y9cIObh0M/Untitled)

<img src="src/readmeIMG2.png" alt="образец дизайна в Figma">

## API

### [API можно прочесть выше](#api-маршруты)
