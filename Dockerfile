FROM python:3.10-slim
LABEL authors="Daniel Rottner"

# Setting the workdir
WORKDIR /app

# Copy relevant code
COPY bacondistance bacondistance/
COPY frontend frontend/
COPY requirements.txt ./

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "bacondistance.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]