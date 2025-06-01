# Use an official Python runtime as a parent image
FROM python:3.12

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv (Python package manager used by mem0-mcp)
RUN pip install uv

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY pyproject.toml uv.lock* ./ 
RUN uv pip install --system -e . --no-cache-dir

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on (default is 8080 for mem0-mcp)
EXPOSE 8080

# Define the command to run the application
CMD ["uv", "run", "main.py", "--host", "0.0.0.0", "--port", "8080"]