# Задача: тесты и TRUNCATE

## Цель

- `conftest`: TRUNCATE порядок с учётом FK; хелпер сида `assignment` для `flow_id`.
- Тесты сдачи: happy 201, `assignment_not_found`, 409 дубликат; снять `skip` с плейсхолдера.
- Диалог: опционально assert двух строк в `dialog_messages` после успешного POST.
