FROM python:3.13

ENV DISCORD_TOKEN=''

WORKDIR /bot
COPY python/ ./
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "bot.py"]
