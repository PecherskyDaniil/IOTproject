# База данных
## Устройства
### devices
* id - int
* device_name - str
* unique_hash - str
* user_id - int
* feed_interval - int
* last_changed - timestamp
### devicedatas
* id - int
* device_id - int
* turbidity - float
* waterlevel - float
* created - timestamp
## Пользователи
### users
* id - int
* chat_id - str
* name - str