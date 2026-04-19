# Задача 01: Логическая модель и сценарии

**Итерация:** [iteration-2-schema](../../plan.md)

## Цель

Расширить [docs/data-model.md](../../../../../../data-model.md): Material, KnowledgeItem, Progress (VIEW); исправить `User.email` (nullable, без DEFAULT); обновить логическую ER-диаграмму. Обновить [docs/spec/user-scenarios.md](../../../../../../spec/user-scenarios.md) — Material в С1/П3, KnowledgeItem в С1.

## Шаги

1. Добавить сущности Material, KnowledgeItem; описать Progress как VIEW `participant_assignment_progress`.
2. В User: email опционален, уникален при наличии значения (физически — `UNIQUE NULLS NOT DISTINCT`).
3. Обновить Mermaid erDiagram (логика).
4. Синхронизировать user-scenarios и сводную таблицу сценариев.

## DoD

- Все новые сущности имеют аннотации сценариев.
- Нет противоречий с итерацией 1 по смыслу сценариев.
