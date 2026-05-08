# task-02: Backend — plan

- `backend/services/data_query.py`: классификация через LLM, whitelist intent, параметрические запросы, лимит 100 строк, лог `correlation_id` + intent.
- `backend/api/data_query_web.py`: `POST /flows/{flow_id}/data-query`, `require_teacher_in_flow`, зависимость `get_llm_client`.
- Схемы в `schemas_web.py`, включение роутера в `router.py`.

# summary

Реализовано по пунктам; см. файлы репозитория.
