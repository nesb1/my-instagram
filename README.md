# Fake Instagram

### Description:
    Бэкенд для инстаграм
    
### Аутенфикация
    
    Должна быть реализована на основе JWT.
    Должна иметь access_token и refresh_token
    По refresh_token можно получить новую пару токенов, тогда старая
    больше не является валидной.
    Каждый раз, когда пользователь входит в систему, старые токены
    сбрасываются и генерируется новая пара (access, refresh).
    Если пользователь залогинился сначала на одном устройстве, 
    а потом на другом, то при попытке обновить информацию на первом его
    должно выкинуть из системы с сообщением, что его токен устарел.
    
    
###Создание постов
    Клиент должен передавать на сервер base64 картинки, описание,
    отмеченных пользователей, название места, где была сделана
    фотография. Если фотография была не квадратная, то сервер делает
    её квадратной и сохраняет в файловую систему, путь сохраняет в БД.
    Обрезание и сохранение фотографии должно выполняться в отельном
    процессе. Передача фотографии в процесс должна происходить через
    redis queue.
    При сохранение в файловую систему надо избежать большого скопления
    файлов/папок(не боольше 1000) в одной папке.
    
    

### Create venv:
    make venv

### Run tests:
    make test

### Run linters:
    make lint

### Run formatters:
    make format

### Build service:
	make build
