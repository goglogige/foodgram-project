# Cайт Foodgram, «Продуктовый помощник»

![Foodgram workflow](https://github.com/goglogige/foodgram-project/actions/workflows/foodgram_workflow.yml/badge.svg)

Онлайн-сервис на котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Используется Continuous Integration и Continuous Deployment.
При пуше в ветку main автоматически отрабатывают сценарии:
1. Автоматический запуск тестов,
2. Обновление образов на Docker Hub,
3. Автоматический деплой на боевой сервер,
4. Отправка сообщения в телеграмм-бот в случае успеха.

## Начало работы

1. Клонируйте репозиторий на локальную машину.
```
git clone <адрес репозитория>
```
2. Для работы с проектом локально - установите вирутальное окружение и восстановите зависимости.
```
python -m venv venv
pip install -r requirements.txt 
```

### Подготовка удаленного сервера для развертывания приложения

Для работы с проектом на удаленном сервере должен быть установлен Docker и docker-compose.

Проверим нет ли старых версий Docker.
Команда удаления старых версий Docker:
```
sudo apt remove docker docker-engine docker.io containerd runc 
```

Если сервер ранее настраивался - убедитесь что порты 8000 и 80 свободны и не используются, проверяем порты командой:
```
sudo ss -tulpn
```
Обновим список пакетов apt: 
```
sudo apt update
```
Установим пакеты, необходимые для загрузки через https:
```
sudo apt install \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg-agent \
  software-properties-common -y
```
Добавим ключ GPG для подтверждения подлинности в процессе установки:
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```
Добавим репозиторий Docker в пакеты apt:
```
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```
Снова обновим индекс пакетов, потому что в apt добавлен новый репозиторий:
```
sudo apt update
```
Установим Docker и docker-compose, запустим демон-процесс и активируем автоматический запуск при загрузке, все одной командой:
```
sudo apt install docker-ce docker-compose -y
```
Проверим что Docker работает:
```
sudo systemctl status docker
```
Установим автозапуск Docker при старте системы:
```
sudo systemctl enable docker
```
Создайте папку проекта на удаленном сервере и скопируйте туда файл переменных окружения .env,
файлы docker-compose.yaml, Dockerfile, host.conf будут скопированы при пуше:
```
scp ./<FILENAME> <USER>@<HOST>:/home/<USER>/dev/foodgram-project/foodgram/
```

### Подготовка репозитория на GitHub

Для использования Continuous Integration и Continuous Deployment необходимо в репозитории на GitHub прописать Secrets - переменные доступа к вашим сервисам.
Переменые прописаны в workflows/foodgram_workflow.yml

* DOCKER_PASSWORD, DOCKER_USERNAME - для загрузки и скачивания образа с DockerHub 
* USER, HOST, PASSPHRASE, SSH_KEY - для подключения к удаленному серверу 
* TELEGRAM_TO, TELEGRAM_TOKEN - для отправки сообщений в Telegram

### Развертывание приложения

1. При пуше в ветку main приложение пройдет тесты, обновит образ на DockerHub и сделает деплой на сервер. Дальше необходимо подлкючиться к серверу.
```
ssh <USER>@<HOST>
```
2. Нам понадобится CONTAINER ID, используем команду для отображения запущенных контейнеров:
```
sudo docker container ps
```
3. Перейдите в запущенный контейнер приложения командой:
```
sudo docker container exec -it <CONTAINER ID> bash
```
4. Внутри контейнера необходимо выполнить миграции и собрать статику приложения:
```
python manage.py collectstatic --no-input
```
```
python manage.py migrate
```
5. Для использования панели администратора по адресу http://0.0.0.0/admin/ необходимо создать суперпользователя.
```
python manage.py createsuperuser
```

## Технологии используемые в проекте
Python, Django, PostgreSQL, Nginx, Docker, GitHub Actions

## Авторы

* **Evgenii Katolichenko** - автор, студент курса Python-разработчик в Яндекс.Практикум. Это учебный проект.
Если есть вопросы или пожелания по проекту пишите на почту - evg.katolichenko@gmail.com

## Благодарности

* Создателям проекта Яндекс.Практикум
* Куратору
* Наставникам
* Код ревьюверу
* Отзывчивым однокурсникам
