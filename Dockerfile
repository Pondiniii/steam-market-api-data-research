# Użyj oficjalnego obrazu Ubuntu jako bazowego
FROM ubuntu:latest

# Aktualizuj system i zainstaluj niezbędne zależności
RUN apt-get update && apt-get install -y \
    postgresql \
    postgresql-contrib \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    sudo \
    gnupg2

# Dodaj repozytorium Windscribe i zainstaluj windscribe-cli
RUN echo "deb https://repo.windscribe.com/ubuntu bionic main" | tee /etc/apt/sources.list.d/windscribe-repo.list && \
    curl https://repo.windscribe.com/keys/windscribe-cli.pub | apt-key add - && \
    apt-get update && \
    apt-get install -y windscribe-cli

# Tworzenie środowiska wirtualnego dla Pythona
RUN python3 -m venv /opt/venv

# Aktywuj wirtualne środowisko i zainstaluj paczki
RUN /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install psycopg2 requests

# Tworzenie katalogu pracy i skopiowanie plików projektu do kontenera
WORKDIR /app
COPY . /app

# Ustawienie środowiska PATH, aby używać wirtualnego środowiska Pythona
ENV PATH="/opt/venv/bin:$PATH"

# Komenda uruchomienia aplikacji
CMD ["python3", "your_script.py"]

