# Итерация 5: Чат с ассистентом (контур виджета) — summary

**Статус:** Done

## Ценность

После входа пользователь открывает плавающий чат на любой странице `(app)` и видит историю диалога; новые сообщения уходят в backend и после перезагрузки подтягиваются из API.

## Реализовано

- **`web/lib/api/types.ts`** — `DialogMessage`, `DialogMessageListPage`, `DialogMessageCreateResponse`.
- **`web/lib/api/dialog.ts`** — `fetchDialogMessages`, `postDialogMessage` (JWT через `apiFetch`).
- **`web/components/chat-panel.tsx`** — загрузка истории, skeleton / empty / ошибка загрузки с retry, optimistic user-сообщение, ответ ассистента из POST, offline-хинт, отправка без логирования содержимого.
- **`web/components/chat-widget-shell.tsx`** — при открытии Sheet: нет сессии → текст «Войдите…»; иначе `ChatPanel`; контент только при `open`.

## Задачи

| Задача | Результат |
|--------|-----------|
| task-01 | Типы и API клиент диалога |
| task-02 | `ChatPanel` |
| task-03 | Интеграция в виджет |
| task-04 | Документация, tasklist, lint/build |

## Ограничения

- Список истории: один запрос `limit=50` — при большой истории на экране только первые до 50 сообщений по курсорной модели backend (см. `plan.md`).

## Проверки

- `npm run lint` и `npm run build` в каталоге `web/`.
