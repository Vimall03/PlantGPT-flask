FROM python:3.12-slim

WORKDIR /app 

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pandoc \
    texlive-xetex \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    lmodern \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .  

# Expose port 5000 for Flask
EXPOSE 5000

# Set environment variable for Flask
ENV FLASK_APP=app.py

# Run Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]