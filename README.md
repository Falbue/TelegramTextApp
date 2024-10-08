**<h1>Telegram-Text-Apps</h1>**
Проект, для быстрого и удобного создания текстовых приложений. По факту, это набор функций, которые делают тоже самое, что Вы могли бы написать сами

**<h2>Текстовое приложение</h2>**
Под текстовым приложением, подразумевается, приложение, которе состоит из одного сообщения и все действия с ботом происходят через __inline-button__

## Подготовка
Для работы **TTA** требуется установка **python**, последней версии
```shell
winget install python
```

Для установки библиотеки через pip, нужно установить git
```shell
winget install --id Git.Git -e --source winget
```

## Установка
```shell
pip install git+https://github.com/Falbue/TelegramTextApp.git
```

## Использование
### Создание приложения
```shell
TTA-create name project api id_admin
```
* [Получение API бота](https://t.me/BotFather)
* [Получение вашего id](https://t.me/getmyid_bot)

### Запуск приложения
Для запуска конкретного приложения:
```shell
TTA name_project
```

Для запуска всех приложений (beta):
```shell
TTA ALL
```

### Дополнительные команды
Обновление кода TTA, если была скачана новая версия библиотеки
```shell
TTA-updata project_name
```

Добавление приложения в автозапуск:
```shell
TTA-autostart project_name
```
