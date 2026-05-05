Fintech MVP (FastAPI + PostgreSQL + Docker Compose)

Минимальный учебный сервис для учета финансовых операций:
- авторизация пользователя;
- создание операций `income`/`expense`;
- просмотр списка операций;
- расчет сводки: доход, расход, баланс.

Стек:
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker Compose

## 1) Запуск проекта

```bash
docker compose up --build -d
```

Проверить состояние контейнеров:

```bash
docker compose ps
```

Ожидается, что `app` и `db` в статусе `Up`.

## 2) Проверка доступности API

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:

```json
{"status":"ok"}
```

Также можно открыть Swagger UI:
`http://localhost:8000/docs`

## 3) Авторизация (получение токена)

Демо-учетные данные:
- username: `demo`
- password: `demo123`

Запрос:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'
```

Ожидаемый ответ:

```json
{"access_token":"demo-token","token_type":"bearer"}
```

Дальше во все защищенные методы передается заголовок:

`Authorization: Bearer demo-token`

## 4) Создание транзакции

Пример дохода:

```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer demo-token" \
  -d '{"tx_type":"income","amount":1000,"description":"salary"}'
```

Пример расхода:

```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer demo-token" \
  -d '{"tx_type":"expense","amount":250,"description":"food"}'
```

Что проверяется:
- `tx_type` принимает только `income` или `expense`;
- `amount` должен быть больше 0;
- запись сохраняется в БД и возвращается с `id` и `created_at`.

## 5) Просмотр списка транзакций

```bash
curl http://localhost:8000/transactions \
  -H "Authorization: Bearer demo-token"
```

Ожидается JSON-массив транзакций.

## 6) Проверка финансовой сводки

```bash
curl http://localhost:8000/summary \
  -H "Authorization: Bearer demo-token"
```

Ожидаемый формат:

```json
{"total_income":"1000.00","total_expense":"250.00","balance":"750.00"}
```

## 7) Что умеет код (чек-лист)

- Поднимается одной командой через Docker Compose.
- Подключается к PostgreSQL и автоматически создает таблицу транзакций при старте.
- Проверяет логин/пароль и возвращает токен.
- Защищает бизнес-эндпоинты через bearer token.
- Валидирует входные данные транзакций.
- Считает агрегаты по доходам/расходам и итоговый баланс.

## 8) Остановка проекта

```bash
docker compose down
```

Если нужно удалить и том БД:

```bash
docker compose down -v
```
