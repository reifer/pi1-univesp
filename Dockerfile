FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Coleta os arquivos estáticos para produção (corrige o problema do alto contraste e CSS)
RUN python manage.py collectstatic --noinput

EXPOSE 10000

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:10000"]