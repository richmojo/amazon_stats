#!/bin/bash

# Ensure the script is running as root
if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

# Update the system
apt-get update

# Install Docker
apt-get install -y docker.io

# Install Docker Compose
apt-get install -y docker-compose

# Change directory to your project folder
cd /root/amazon_data

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    touch .env
fi

# Set up cron job for update.sh script
(crontab -l 2>/dev/null; echo "@reboot /root/amazon_data/update.sh") | crontab -

# Ensure update.sh is executable
chmod +x /root/amazon_data/update.sh