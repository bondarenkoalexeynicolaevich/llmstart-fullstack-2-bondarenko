# Итерация 4: Лидерборд — summary

**Статус:** ✅ Done

## Ценность

После входа участник потока открывает `/leaderboard` и видит рейтинг: таблица с прогрессом, статусами по урокам и медалями топ-3 либо диаграмму рассеяния с теми же данными (`GET /v1/flows/{flow_id}/leaderboard`).

## Реализовано

- **`web/lib/api/types.ts`** — типы `LeaderboardResponse`, строки, точки scatter, `ScatterMeta`, `LessonStatusIcon`.
- **`web/lib/api/flow-teacher.ts`** — `fetchFlowLeaderboard(flowId)`.
- **`web/components/leaderboard-client.tsx`** — переключатель «Таблица / Карта», skeleton / empty / error + retry, обновление без потери данных (opacity при `busy`).
- **`web/app/(app)/leaderboard/page.tsx`** — рендер `LeaderboardClient`.

## Задачи

| Задача | Результат |
|--------|-----------|
| task-01 | Типы и клиент API |
| task-02 | Таблица, прогресс-бар, иконки уроков, медали |
| task-03 | Recharts `ScatterChart`, топ-3 крупнее и цветом |
| task-04 | Маршрут, lint/build, tasklist, summary |

## Отклонения от плана

- Вместо отдельного shadcn Tabs — группа кнопок с `role="tablist"` / `role="tab"` (KISS, без новых UI-зависимостей).
- Отдельные `summary.md` в папках задач не создавались — итог в этой таблице.

## Проверки

- `npm run lint` и `npm run build` в каталоге `web/`.
