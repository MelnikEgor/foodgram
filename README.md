# Описание:

Проект `foodgram`, представляет из себя реализацию контейнерезации проекта для локального запуска или деплоя на удаленный сервер.

В качестве информации о __котике__, доступно размещение его фото.

Площадка позволяет просматривать карточки __котиков__ других пользователей, размещение/редактирование/удаление информации о собственных __котиках__.

Ресурс требует регистрации пользователей для просмотра информации.

Доступ к карточкам __котиков__ доступна только аутентифицированным пользователям.

# Как запустить backend проект локально:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/MelnikEgor/foodgram.git
```

```
cd backend
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```
> [!IMPORTANT]  
> Если у вас Linux/macOS используетй в заместо `python` -> `python3`.
> Все представленые команды будут для Windows системы, если не будет кардинальных отличий.

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас Windows

    ```
    source venv/Scripts/activate
    ```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Вы можете выбрать с какой СУБД вам работать. Стандартной `SQLite` или `PostgreSQL` (`все необходимые зависимости установлены`).
Загляните в файл `backend/settings.py`, посмотрите как созадется словарь `DATABASES`.
Если решите использовать СУБД `SQLite`, то в файле `.env`, который создается по примеру файла `.env.example`, переменную `DBMS_POSTGRES`, оставить пустой.

> [!IMPORTANT]
> Для локального развертывания проекта можно использовать СУБД `SQLite`.

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

# Запуск проекта через Docker.Как запустить проект локально:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/MelnikEgor/foodgram.git
```

Для контейниризации, на ПК должен быть установлен Docker.

## Как запустить проект локально:

В терминале, перейдите в корневую директорию проекта `foodgram`.

Создайте файл `.env` по примеру `.env.example`.

Выполните команду:

```
docker compose -f docker-compose.yml up --build
```
* `docker compose` - команда указывающая, что работаем с __оркестром__ контейнеров.
* `-f docker-compose.yml` - ключ, для явного указания имени файла, по которому требуется собрать __орекстр__ контейнеров.
* `up` - создание и запуск __оркестра__ контейнеров.
* `--build` - команда сборки образов по инструкциям из Dockerfile`ов, для каждого контейнера.

Откройте второй терминал в корневой директории проекта. Потребуется выполнить команды перен началом работы.

> [!IMPORTANT]
> docker compose -f <имя_файла> exec <имя_контейнера> <команда>
> * `exec <имя_контейнера>` - указывает, что требуется выполнить в терминале в нутри контейнера, указанную команду.
> * `<команда>` - указывается команда, которую требуется выполнить.

```
docker compose -f docker-compose.yml exec backend python manage.py migrate
docker compose -f docker-compose.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

Можете проверить работу по `localhost:8000` в браузере.

Также осуществить локальный запуск возможно другим способом. Он похож на способ запуска на сервере, за исключением некоторых шагов, расмотрим их в пункте **Как запустить проект на сервере**.

## Как запустить проект на сервере:

На сервере должен быть установле `Nginx`, в конфигурации требуется настроить перенаправления 80 порта на 9000.

Подключаетесь к серверу.

> [!IMPORTANT]
> На сервере, также требуется установить Docker.

Требуется создать директорию для проекта, например __foodgram__.

Перейдите в данную директорию

```
cd foodgram
```

В директории вам требуется создать файл `.env`, как вы уже делали в разделе **Как зпустить проект локально**.
Также в данную директорию требуется скопировать файл `docker-compose.production.yml`, который лежит в корневой директории проекта на локальной машине.

После того, как все файлы созданы, выполняете команду:

```
sudo docker compose -f docker-compose.production.yml up -d
```

> [!IMPORTANT]
> `sudo` - говорит терминалу Linux, что команда выполняется с правами администратора, при развертывании на локальной машине, данная команда не требуется.

`-d` - ключ, позволяющий запустить `docker compose` в режиме демона, и будет доступен этот же терминал для дальнейшей работы.

> [!IMPORTANT]
> Основные команды, которые вам понадобятся для управления:
> * `docker compose stop` — остановит все контейнеры, но оставит сети и volume. Эта команда пригодится, чтобы перезагрузить или обновить приложения.
> * `docker compose down` — остановит все контейнеры, удалит их, сети и анонимные volumes. Можно будет начать всё заново.
> * `docker compose logs` — просмотр логов запущенных контейнеров.

Если проект разворачивался локально, то проверьте доступ по `localhost:8000` в браузере.
Если проект разворачивался на удаленном сервере, то доусп осуществляется по вашему домену `https:/<имя_домена>/`.

# Разработчики:

Егор Мельник.
* Реализация `backend` проекта `foodgram`.
* Реализация контейнерезации готового проекта на Django.
* Деплой и развертывание проекта на удаленый сервер.

# Технологии:

- django framework 
- Django Rest Framework 
- Python 
- sqlite
- PostgreSQL
- Gunicorn
- Nginx
- Djoser
- dotenv 