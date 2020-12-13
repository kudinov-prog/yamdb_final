![Yamdb_final](https://github.com/kudinov-prog/yamdb_final/workflows/Yamdb-final-workflow/badge.svg)

# API YAMDB

Api для сервиса YAMDB каталога произведений и отзывов на них.

Сервис представляет собой web-приложение с базой данных на PostgreSQL.

### Установка

1. Подготовка

    Приложение работает за счет [Docker](https://docs.docker.com/engine/install/) и [docker-compose](https://docs.docker.com/compose/install/)
    
    Установка для разных операционных систем описана в инструкциях по ссылкам выше

2. Запуск сервиса
    
    Приложение работает в двух docker контейнерах, для сборки и запуска всего окружения необходимо выполнить комманду
 
    ```
    docker-compose up
   ```
    
### Первоначальная настройка

1. Предварительная миграция (создание таблиц в БД)

    ```
    docker-compose run web python manage.py migrate
    ```

2. Создание суперпользователя
    ```
   docker-compose run web python manage.py createsuperuser
   ```
3. Загрузка демонстрационных данных
    ```
   docker-compose run web python manage.py loaddata fixtures.json
   ```
4. Документация на API 

     Документация после запуска приложения будет доступна по адресу 
    ```
    http://localhost:8000/redoc
    ```


### Используемый стек
* [Python](https://www.python.org/) 
* [Django](https://www.djangoproject.com/) 
* [Django-restframework](https://www.django-rest-framework.org/)
* [Docker](https://www.docker.com/)
* [Docker-compose](https://docs.docker.com/compose/)
* [Postgresql](https://www.postgresql.org/)


### Автор
Морозов Дмитрий <inood@yandex.ru>
данный проект создан в рамках обучения на курсах Yandex-Praktikum 