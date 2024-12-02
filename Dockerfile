FROM python:3.11

# Set the working directory in the container
WORKDIR /amazon_stats

# First, add only the requirements.txt to leverage Docker cache
COPY requirements.txt /amazon_stats/
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

# Copy the current directory contents into the container at /amazon_stats
COPY . /amazon_stats

# Add cron jobs
RUN echo "0,30 * * * * python /amazon_stats/sync_process.py" >> /etc/cron.d/amazon_stats_cron \
    && echo "15,45 * * * * python /amazon_stats/merge_process.py" >> /etc/cron.d/amazon_stats_cron \
    && echo "5 * * * * python /amazon_stats/delete_process.py" >> /etc/cron.d/amazon_stats_cron \
    && chmod 0644 /etc/cron.d/amazon_stats_cron \
    && crontab /etc/cron.d/amazon_stats_cron

# Run cron in the foreground
CMD ["cron", "-f"]



