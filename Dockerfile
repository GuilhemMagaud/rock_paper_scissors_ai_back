# Utiliser une image Python avec la version spécifiée
ARG PYTHON_VERSION=3.10.7
FROM python:${PYTHON_VERSION}

# Définir le dossier de travail
WORKDIR /app

# Copier le code source de l'application
COPY . .

# Installer les dépendances
RUN pip install -r requirements.txt

# Exposer les ports (si besoin pour Flask, FastAPI, etc.)
EXPOSE 5000

# Commande pour lancer l'application (modifie selon ton projet)
CMD ["python", "app.py"]
