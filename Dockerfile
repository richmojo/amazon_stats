FROM python:3.11

# Set the working directory in the container
WORKDIR /amazon_stats

# First, add only the requirements.txt to leverage Docker cache
COPY requirements.txt /amazon_stats/
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the current directory contents into the container at /amazon_stats
COPY . /amazon_stats

# Default command (will be overridden by docker-compose)
CMD ["python", "/amazon_stats/main.py"]



