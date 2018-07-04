# Инcтрукция по развертыванию системы

## Предварительные требования

Для выполнения следующих работ исполнитель должен уметь:

- устанавливать дистрибутивы семейства Linux
- знание базовых операций с помощью интерфейса коммандной строки
  - перемещение по файловой системе
  - создание, копирование, удаление файлов
  - редактирование тектовых файлов
  - создание, удаление, изменение учетных записей
  - запуск, остановка, проверка статуса сервисов 
  - опыт работы с пакетным менеджером yum

Для выполнения исполнителю потребуется учетная запись root или учетная запись с возможностью запуска комманд с аналогичными правами через sudo

Для запуска окружения рекомендуется использовать аппаратную платформу с поддержкой виртуализации. 

Виртуальной машине рекомендуется выделить не менее 1Гб ОЗУ.

## Установка базовой системы

1. Скачайте образ ОС Centos 7 c любого подходящего зеркала. Список всех оффициальных зеркал находится по следующему адресу [CentOS Mirror](http://isoredirect.centos.org/centos/7/isos/x86_64/CentOS-7-x86_64-Minimal-1804.iso)

2. Установите систему в редакции **minimal**

3. Обновите пакеты системы:

```
    $ sudo yum update
```

## Подготовка веб-приложения

1. Устанавите репозитарий Extra Packages for Enterprise Linux (EPEL):

```
    $ sudo yum install epel-release
```

2. Усатнавите пакеты nginx, tomcat, java, policycoreutils-python:

```
    $ sudo yum install nginx tomcat tomcat-webapps tomcat-admin-webapps java-1.8.0-openjdk policycoreutils-python
```

3. Создайте файл конфигурации nginx:

```
    $ sudo touch /etc/nginx/conf.d/tomcat.conf
```

4. Добавьте в созданный файл следующие строки:

```
server {
        listen  80;
        server_name <tomcat.name>;
        location / {
        proxy_pass http://localhost:8080;
        }
}
```

*Примечание: <tomcat.name> - FQDN по которому будет обрабатываться запрос на доступ к tomcat, поэтому он должен быть прописан или в dns-зоне, обслуживающую соответстсвующую сеть, или в файле hosts источника запросов*

5. Добавьте разрешение на доступ соединений к порту *80* из сети в настройки файрволла: 

```
    $ sudo firewall-cmd --permanent --zone=public --add-service=http
    $ sudo firewall-cmd --reload
```

6. Добавьте разрешение SELinux для перенаправления соединений от nginx к tomcat:

```
    $ sudo setsebool -P httpd_can_network_relay 1
```

7. Для доступа к панели администрирования tomcat в файле **/usr/share/tomcat/conf/tomcat-users.xml** раскомментируйте следующие строки (кроме поля "<user name...", его добавьте вручную):

```
    <role rolename="admin-gui"/>
    <role rolename="manager-gui"/>
    <role rolename="manager-status"/>
    <user name="<admin_name>" password="<admin_password>" roles="admin-gui,manager-gui,manager-status" />
```

*Примечание: значения <admin_name> и <admin_password> необходимо задать согласно вашим требованиям*

8. Запустите и включите автоматическую загрузку сервисов nginx и tomcat:

```
    $ sudo systemctl enable tomcat.service
    $ sudo systemctl start tomcat.service
    $ sudo systemctl enable nginx.service
    $ sudo systemctl start nginx.service
```

## Подготовка веб-сервиса для работы с БД

1. Установить пакеты httpd mod_wsgi postgresql-server python-psycopg2 git

```
    $ sudo yum install httpd mod_wsgi postgresql-server python-psycopg2 python-flask git
```

2. Заменить значение порта на **81** в файле /etc/httpd/conf/httpd.conf:

```
Listen 81
```

3. Разрешить доступ к TCP порту 81:

```
    $ sudo firewall-cmd --permanent --zone=public --add-port=81/tcp
    $ sudo firewall-cmd --reload
```

4. Запустите и включите автоматическую загрузку сервиса httpd:

```
    $ sudo systemctl enable httpd.service
    $ sudo systemctl start httpd.service
```

5. Перейдите в каталог /var/www и скачайте приложение с github:

```
  $ cd /var/www
  $ git clone https://github.com/ivnahgm/simpleapp.git
```

6. Создайте кластер postgresql:

```
    $ postgresql-setup initdb
```

7. В файле */var/lib/pgsql/data/pg_hba.conf* заменити в следующей строке значение **indent**:

```
host    all             all             127.0.0.1/32            indent
```

на **md5**:

```
host    all             all             127.0.0.1/32            md5
```

8. Запустите и включите автоматическую загрузку сервиса postgresql:

```
    $ systemctl enable postgresql.service
    $ systemctl start postgresql.service
```

9. Создайте базу данных, пользователя и назначьте ему необходимые права:

```
    $ sudo -u postgres createdb <db_name>
    $ sudo -u postgres createuser -P <db_user>
    $ sudo -u postgres psql -c "grant all privileges on database <db_name> to <db_user>;"
```

*Примечание: значения <db_name> и <db_user> необходимо задать согласно вашим требованиям*

10. Импортируйте схему для созданной базы данных:

```
    $ sudo -u postgres psql -U <db_user> -d <db_name> -h localhost < /var/www/simpleapp/initdata/schema.sql
```

11. Заполните значения в файле /var/www/simpleapp/settings.py значениями, полученными на предыдущих шагах:

```
DBNAME = '<db_name>' #имя базы данных
DBUSER = '<db_user>' #пользователь базы данных
DBPASS = '<db_password>' #пароль пользователя базы данных
```

12. Запустите скрипт для первичного наполнения созданной базы данных:

```
    $ cd /var/www/simpleapp
    $ python fill_db.py
```

13. Создайте пользователя от которого будет запускаться wsgi-приложение:

```
    $ useradd -M -s /bin/false -G apache flask
    $ usermod -L flask
```

14. Создайте файл /etc/httpd/conf.d/simpleapp.conf  со следующим содержимым:

```
<VirtualHost *>
    ServerName simpleapp.test

    WSGIDaemonProcess simpleapp user=flask group=apache threads=5
    WSGIScriptAlias / /var/www/simpleapp/simpleapp.wsgi

    <Directory /var/www/simpleapp>
        WSGIProcessGroup simpleapp
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>
```

15. Добавьте разрешение в SELinux:

```
    $ sudo setsebool -P httpd_can_network_connect on
```

16. Задайте владельца и группу на папку /var/www/simpleapp:

```
  $ chown -R flask:apache /var/www/simpleapp
```

17. Перезапустите сервис httpd:

```
  $ sudo systemctl restart httpd
```

## Устранение неисправностей

Для диагностики рекомендуется:

- Использовать просмотр журнала работы сервисов:

```
  $ sudo journalctl -u <service_name>
```

- Просмотр текущего сотояния сервиса:

```
  $ sudo systemctl status <service_name>
```

- Отключить службу firewalld:

```
  $ sudo systemctl stop firewalld
```

- Отключить SELinux:

```
  $ sudo setenforce 0
```

- Просмотр журналов запросов httpd /var/log/httpd/*

- Просмотр журналов запросов nginx /var/log/nginx/*

- Просмотр журналов SELinux /var/log/audit/audit.log