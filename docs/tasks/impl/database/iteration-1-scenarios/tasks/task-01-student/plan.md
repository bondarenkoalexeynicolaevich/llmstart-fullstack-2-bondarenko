# Задача 01: Сценарии студента

**Итерация:** [iteration-1-scenarios](../../plan.md)

## Цель

Описать 3 сценария для студента (бот и/или веб на уровне намерений) и явно указать участвующие сущности из `docs/data-model.md`.

## Результат

Раздел «Студент» в [docs/spec/user-scenarios.md](../../../../../../spec/user-scenarios.md):

| ID | Название | Канал | Сущности |
|----|----------|-------|----------|
| С1 | Вопрос ассистенту | Telegram-бот | Flow, Participant, DialogMessage |
| С2 | Фиксация выполнения задания | Telegram-бот | Lesson, Assignment, Participant, Submission |
| С3 | Просмотр прогресса | Веб | Flow, Module, Lesson, Assignment, Participant, Submission |

## Проверка

- Текст без API, БД, названий эндпоинтов.
- Маппинг согласован с таблицей сущностей в `data-model.md`.
