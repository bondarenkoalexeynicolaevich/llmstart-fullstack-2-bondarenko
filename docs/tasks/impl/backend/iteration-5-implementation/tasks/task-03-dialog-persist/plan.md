# Задача: персистентность диалога

## Цель

Сервис: резолв участника → история (лимит N) → INSERT user → LLM → INSERT assistant → commit; реальные UUID в ответе. `api/dialog.py` — тонкий слой, логи без `content`.
