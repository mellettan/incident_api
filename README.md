# Incident API

Простой API для работы с инцидентами.

## Запуск

1. Клонируем репозиторий:

```bash
git clone https://github.com/Mellettan/incident_api
cd incident_api
````

2. Устанавливаем зависимости через Poetry:

```bash
poetry install --no-root
```

3. Запускаем приложение:

```bash
poetry run uvicorn src.main:app --reload
```

API будет доступно по адресу: `http://127.0.0.1:8000`.

---

## Эндпоинты

### Создание инцидента

**POST** `/incidents/`

![1.png](report_images/1.png)

---

### Получение списка инцидентов

**GET** `/incidents/`

![2.png](report_images/2.png)

---

### Обновление статуса инцидента

**PATCH** `/incidents/{id}`

![3.png](report_images/3.png)

---
## Тестирование

Покрытие тестами - 96%. Все ключевые функции протестированы.

![test.png](report_images/test.png)