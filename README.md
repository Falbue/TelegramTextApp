**<h1>Telegram-Text-Apps</h1>**
Проект, для быстрого и удобного создания текстовых приложений. По факту, это набор функций, которые делают тоже самое, что Вы могли бы написать сами

**<h2>Текстовое приложение</h2>**
Под текстовым приложением, подразумевается, приложение, которе состоит из одного сообщения и все действия с ботом происходят через __inline-button__

## Установка
```shell
pip install git+https://github.com/Falbue/TelegramTextApp.git
```

## Использование
```python
from TelegramTextApp import TTA

BOT_API = ''
ID_ADMIN = 0
FOLDER = 'data' 

TTA(BOT_API, ID_ADMIN, FOLDER)
```
