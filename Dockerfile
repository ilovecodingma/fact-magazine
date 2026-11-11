# 사이트 제공 + API 서버(server/app.py). 파이썬 기본 기능 + PostgreSQL 드라이버(pg8000, 순수 파이썬)만 이 상자 안에 깔립니다 — 내 PC 의 파이썬에는 아무것도 깔지 않습니다.
FROM python:3.12-slim
RUN pip install --no-cache-dir pg8000==1.31.2
WORKDIR /app
COPY server/app.py /app/app.py
ENV HOST=0.0.0.0 PORT=8080 SITE_DIR=/site DATA_DIR=/data
EXPOSE 8080
CMD ["python", "-u", "/app/app.py"]
