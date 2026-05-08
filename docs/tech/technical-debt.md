# Технический долг — Frontend

Результат ревью качества кода в рамках **Итерации 7** (tasklist-frontend.md).  
Дата: 2026-05-08.  
Инструменты проверки: `vercel-react-best-practices`, `nextjs-app-router-patterns`, `shadcn`.

---

## P1 — Критично (блокирует производительность/архитектуру)

### ~~TD-001~~ · ✅ ИСПРАВЛЕНО · Recharts без динамической загрузки (bundle-dynamic-imports)

**Файлы:** `components/teacher-dashboard-client.tsx`, `components/leaderboard-client.tsx`  
**Проблема:** `recharts` (~350 KB min+gz) импортирован статически на верхнем уровне обоих файлов. Библиотека попадает в основной JS-бандл соответствующих маршрутов и блокирует первоначальный рендер, даже если пользователь не смотрит на график.  
**Решение:** Вынести графики в отдельные компоненты, загружаемые через `next/dynamic` с `{ ssr: false }` и `loading` skeleton.

```tsx
const ActivityLineChart = dynamic(
  () => import("@/components/charts/activity-line-chart"),
  { ssr: false, loading: () => <PulseBlock className="h-64 w-full" /> },
);
```

---

### TD-002 · Вся выборка данных — клиентская, без RSC (nextjs-app-router-patterns)

**Файлы:** `app/(app)/dashboard/page.tsx`, `app/(app)/leaderboard/page.tsx`, `app/(app)/chat/page.tsx`  
**Проблема:** Страницы — Server Components только номинально: они сразу рендерят полностью клиентский компонент. Начальный HTML приходит пустым, данные грузятся в `useEffect`. Время до интерактивности увеличено на один RTT (client → server → client).  
**Первопричина:** Сессия хранится в `localStorage` (недоступен на сервере), поэтому авторизованные запросы с сервера невозможны без переосмысления auth-слоя.  
**Решение (долгосрочно):** Перенести сессию в `httpOnly cookie` → использовать Server Components для начальной выборки + streaming Suspense. Это потребует отдельного ADR.  
**Краткосрочно:** Зафиксировать как архитектурный компромисс в ADR, добавить `loading.tsx` на каждый маршрут (см. TD-005).

---

### ~~TD-003~~ · ✅ ИСПРАВЛЕНО · Каскадные `useEffect` — двухшаговый waterfall (async-defer-await)

**Файлы:** `components/teacher-dashboard-client.tsx`, `components/leaderboard-client.tsx`  
**Проблема:** Первый `useEffect` загружает сессию из `localStorage` через `queueMicrotask`, затем четыре отдельных `useEffect` следят за изменением `flowId`/`isTeacher` и запускают fetch. На каждый рендер-цикл: рендер с `session=null` → эффект ставит сессию → перерендер → 4 эффекта запускают fetch. Итого минимум 2 тика до начала сетевых запросов.  
**Решение:** Читать сессию синхронно в `useState` initializer (`useState(() => getSession())`); убрать промежуточный `queueMicrotask` для сессии. Параллельные fetch-ы уже корректны.

```tsx
// Было
const [session, setSession] = useState<WebClientSession | null>(null);
useEffect(() => { queueMicrotask(() => setSession(getSession())); }, []);

// Станет
const [session] = useState<WebClientSession | null>(() => getSession());
```

---

## P2 — Высокий приоритет

### ~~TD-004~~ · ✅ ИСПРАВЛЕНО · `SessionGate` — FOUC и ненадёжный клиентский редирект

**Файл:** `components/session-gate.tsx`  
**Проблема:** Компонент всегда рендерит «Загрузка…» на первый кадр, затем в `useEffect` либо редиректит через `window.location.replace`, либо устанавливает `ready=true`. Пользователь видит мигание пустого экрана при каждом переходе. Использование `window.location` обходит prefetch и soft-navigation Next.js.  
**Решение:** Заменить `window.location.replace` на `router.replace('/login')` из `next/navigation`. Или переместить auth-guard в Next.js Middleware (предпочтительно при переходе на cookie-сессии).

---

### ~~TD-005~~ · ✅ ИСПРАВЛЕНО · Отсутствуют `loading.tsx` на маршрутах (nextjs-app-router-patterns)

**Файлы:** `app/(app)/dashboard/`, `app/(app)/leaderboard/`, `app/(app)/chat/`  
**Проблема:** Нет файлов `loading.tsx`. Suspense-стриминг не используется — skeleton реализован вручную внутри компонентов как проверки `*Loading` state. При навигации между страницами нет встроенного loading UI.  
**Решение:** Добавить `loading.tsx` в каждый маршрут с подходящим skeleton.

---

### ~~TD-006~~ · ✅ ИСПРАВЛЕНО · `PulseBlock` дублирован в двух файлах (shadcn · composition)

**Файлы:** `components/teacher-dashboard-client.tsx` (строки 139–148), `components/leaderboard-client.tsx` (строки 86–90)  
**Проблема:** Идентичный компонент `PulseBlock` с `animate-pulse` определён дважды. Shadcn предоставляет компонент `Skeleton` для этой цели.  
**Решение:** Установить `npx shadcn@latest add skeleton`, заменить оба `PulseBlock` на `<Skeleton className="..." />`, удалить дубли.

---

### ~~TD-007~~ · ✅ ИСПРАВЛЕНО · Ошибки отображаются кастомными `div`, а не `Alert` (shadcn · composition)

**Файлы:** `teacher-dashboard-client.tsx` (строки 387–393, 463–476, 541–553, 665–673), `leaderboard-client.tsx` (строки 218–229), `chat-panel.tsx` (строки 49–69), `login-form.tsx`  
**Проблема:** Блоки ошибок реализованы вручную через `div` с `border-destructive`. Shadcn имеет компонент `Alert` / `AlertDescription` для callout-ов.  
**Решение:** Установить `npx shadcn@latest add alert`, заменить кастомные error-блоки.

---

### ~~TD-008~~ · ✅ ИСПРАВЛЕНО · Статусы сдач — кастомный `span`, а не `Badge` (shadcn · composition)

**Файл:** `components/teacher-dashboard-client.tsx` (строка 589–591)  
**Проблема:**
```tsx
<span className="rounded-md bg-muted px-2 py-0.5 text-xs">
  {STATUS_LABEL[row.status]}
</span>
```
Shadcn предоставляет `Badge` с вариантами для такого паттерна.  
**Решение:** Установить `npx shadcn@latest add badge`, использовать `<Badge variant="secondary">`.

---

## P3 — Средний приоритет

### ~~TD-009~~ · ✅ ИСПРАВЛЕНО · Иконки в `Button` без `data-icon` (shadcn · icons)

**Файлы:** `components/app-shell.tsx` (строка 56, 84), `components/leaderboard-client.tsx` (строки 209–213), `components/teacher-dashboard-client.tsx` (строки 390, 469, 549, 668)  
**Проблема:** Иконки внутри `Button` имеют явные классы размера (`className="size-4"`, `className="mr-1 size-4"`) и передаются без атрибута `data-icon`. По shadcn-правилам компонент сам управляет размером иконок через CSS.  
**Решение:** Убрать классы размера с иконок, добавить `data-icon="inline-start"` или `data-icon="inline-end"`.

---

### ~~TD-010~~ · ✅ ИСПРАВЛЕНО · `space-y-*` вместо `flex flex-col gap-*` (shadcn · styling)

**Файлы:** `components/login-form.tsx` (строки 124, 126, 136), `components/teacher-dashboard-client.tsx` (строки 334, 366, 385, 461, 538, 663), `components/leaderboard-client.tsx` (строки 165, 237–238)  
**Проблема:** Повсеместно используется `space-y-*` для вертикальных стеков. По правилам shadcn следует использовать `flex flex-col gap-*`.  
**Решение:** Заменить `space-y-N` на `flex flex-col gap-N` там, где нет иного контекста.

---

### ~~TD-011~~ · ✅ ИСПРАВЛЕНО · Форма в `LoginForm` без `FieldGroup`/`Field` (shadcn · forms)

**Файл:** `components/login-form.tsx`  
**Проблема:** Поля формы обёрнуты в `<div className="space-y-2">` с `Label` + `Input` напрямую. По shadcn-правилам форм нужны `FieldGroup` + `Field` + `FieldLabel`.  
**Решение:** Рефакторить поля формы по shadcn-шаблону `Field`.

---

### ~~TD-012~~ · ✅ ИСПРАВЛЕНО · `!size-14` с `!important` в `ChatWidgetShell` (shadcn · styling)

**Файл:** `components/chat-widget-shell.tsx` (строка 22)  
**Проблема:** `className="fixed bottom-6 right-6 z-50 !size-14 rounded-full shadow-lg"` — использование модификатора `!` (important) в Tailwind — признак конфликта стилей с компонентом.  
**Решение:** Разобраться, почему `size="icon-lg"` недостаточно для нужного размера, и исправить либо через вариант кнопки, либо через `asChild`.

---

### ~~TD-013~~ · ✅ ИСПРАВЛЕНО · Inline arrow function в `shape` prop Scatter (rerender-no-inline-components)

**Файл:** `components/leaderboard-client.tsx` (строка 368–370)  
**Проблема:**
```tsx
shape={(dotProps: ScatterDotProps) => <ScatterDotShape {...dotProps} />}
```
Новая функция создаётся при каждом рендере — Recharts будет перерисовывать все точки.  
**Решение:** Вынести в стабильный ref или использовать `ScatterDotShape` напрямую как `shape={ScatterDotShape}` при совместимости пропсов.

---

### ~~TD-014~~ · ✅ ИСПРАВЛЕНО · `ChatPage` с `"use client"` на уровне страницы

**Файл:** `app/(app)/chat/page.tsx`  
**Проблема:** Директива `"use client"` добавлена прямо в файл страницы, хотя страница могла бы оставаться Server Component-обёрткой, которая рендерит клиентский `ChatPanel`. Это расширяет клиентский бандл без необходимости.  
**Решение:** Убрать `"use client"` из `page.tsx`; `ChatPanel` уже является Client Component.

---

### ~~TD-015~~ · ✅ ИСПРАВЛЕНО ранее · `Intl.DateTimeFormat` создаётся при каждом вызове (js-cache-function-results)

**Файл:** `components/teacher-dashboard-client.tsx` (строки 70–98)  
**Проблема:** Функции `formatDate`, `formatDateTime`, `formatDayLabel` создают новый экземпляр `Intl.DateTimeFormat` при каждом вызове. В таблицах с десятками строк это излишняя нагрузка.  
**Решение:** Вынести форматтеры на уровень модуля:
```tsx
const DATE_FMT = new Intl.DateTimeFormat("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" });
```

---

## P4 — Низкий / Backlog

### ~~TD-016~~ · ✅ ИСПРАВЛЕНО · Нет route-level metadata (nextjs-app-router-patterns · SEO)

Страницы `dashboard`, `leaderboard`, `chat` не экспортируют `metadata`. Сейчас не критично (приложение закрыто за логином), но нужно для корректного заголовка вкладки и будущего PWA.

---

### ~~TD-017~~ · ✅ ИСПРАВЛЕНО · Нет `eslint-plugin-react-hooks`, eslint-disable в коде

**Файл:** `components/login-form.tsx` (строка 45)  
`// eslint-disable-next-line react-hooks/exhaustive-deps` — признак того, что в `devDependencies` нет `eslint-plugin-react-hooks` (или он не включён в `eslint-config-next`). Нужно проверить конфигурацию ESLint и по возможности убрать disable-комментарий.

---

### ~~TD-018~~ · ✅ ИСПРАВЛЕНО ранее · `cn()` без условной логики — лишняя обёртка

**Файл:** `components/teacher-dashboard-client.tsx` (строки 349–355)  
```tsx
className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
```
`cn()` здесь не нужен — нет условных классов. Можно использовать `buttonVariants(...)` напрямую.

---

### ~~TD-019~~ · ✅ ИСПРАВЛЕНО · DEMO_USER / DEMO_FLOW захардкожены в production-коде

**Файл:** `components/login-form.tsx` (строки 22–23)  
Демо-значения `bondarenko_alexey_nikolaevich` и UUID потока вшиты в код. Следует вынести в `NEXT_PUBLIC_DEMO_*` переменные окружения или убрать из production build.

---

### ~~TD-020~~ · ✅ ИСПРАВЛЕНО · Нет `loading.tsx` и `error.tsx` для `(app)` layout

Не настроен глобальный Error Boundary через `error.tsx` для защищённого сегмента `(app)`. При непойманном исключении в Server Component пользователь увидит страницу ошибки Next.js без возможности восстановления.

---

## Сводная таблица

| ID | Приоритет | Источник правила | Файл(ы) | Усилие |
|----|-----------|-----------------|---------|--------|
| ~~TD-001~~ ✅ | P1 | bundle-dynamic-imports | teacher-dashboard-client, leaderboard-client | S |
| TD-002 | P1 | nextjs: RSC / data fetching | app/**/page.tsx | XL (ADR) |
| ~~TD-003~~ ✅ | P1 | async-defer-await | teacher-dashboard-client, leaderboard-client | XS |
| ~~TD-004~~ ✅ | P2 | nextjs: routing | session-gate.tsx | S |
| ~~TD-005~~ ✅ | P2 | nextjs: loading.tsx | app/**/ | S |
| ~~TD-006~~ ✅ | P2 | shadcn: Skeleton | teacher-dashboard-client, leaderboard-client | XS |
| ~~TD-007~~ ✅ | P2 | shadcn: Alert | teacher-dashboard-client, leaderboard-client, chat-panel, login-form | S |
| ~~TD-008~~ ✅ | P2 | shadcn: Badge | teacher-dashboard-client | XS |
| ~~TD-009~~ ✅ | P3 | shadcn: icons | app-shell, leaderboard-client, teacher-dashboard-client | S |
| ~~TD-010~~ ✅ | P3 | shadcn: styling | login-form, teacher-dashboard-client, leaderboard-client | S |
| ~~TD-011~~ ✅ | P3 | shadcn: forms | login-form | S |
| ~~TD-012~~ ✅ | P3 | shadcn: !important | chat-widget-shell | XS |
| ~~TD-013~~ ✅ | P3 | rerender-no-inline-components | leaderboard-scatter-chart | XS |
| ~~TD-014~~ ✅ | P3 | nextjs: "use client" scope | chat/page.tsx | XS |
| ~~TD-015~~ ✅ | P3 | js-cache-function-results | teacher-dashboard-client | XS |
| ~~TD-016~~ ✅ | P4 | nextjs: metadata | app/**/ | XS |
| ~~TD-017~~ ✅ | P4 | eslint-react-hooks | login-form | XS |
| ~~TD-018~~ ✅ | P4 | shadcn: cn() | teacher-dashboard-client | XS |
| ~~TD-019~~ ✅ | P4 | best practice | login-form | XS |
| ~~TD-020~~ ✅ | P4 | nextjs: error.tsx | app/(app)/ | XS |
