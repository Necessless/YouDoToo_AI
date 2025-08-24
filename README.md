FullStack Pet-проект ToDo приложения с AI.
(SPA + API).
Frontend: React.
Backend: FastAPI, Postgresql, Redis (кеширование и вайтлист рефреш токенов).
AI: Fine-tuned flan/T5-base модель для предсказания подзадач по названию задачи.
Авторизация сделана на основе JWT токенов с access (30 минут) и refresh (30 суток).
Актуальные refresh токены хранятся в redis, что даёт дополнительную гибкость и безопасность.
Проект в процессе разработки.
