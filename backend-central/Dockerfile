# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 (Google Cloud Run default)
EXPOSE 8080

# Command to start your FastAPI app
CMD ["python3", "-m", "src.main"]

