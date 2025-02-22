FROM python:3.12-alpine

ENV APP_HOME=/app

WORKDIR $APP_HOME

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# Створюємо директорію для збереження data.json (якщо її немає)
RUN mkdir -p $APP_HOME/storage

# Визначаємо volume для збереження файлу за межами контейнера
VOLUME ["/app/storage"]

EXPOSE 3000

CMD ["python3", "main.py"]