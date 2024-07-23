FROM python:3.11


# Set the working directory in the container
WORKDIR /amazon_data

# First, add only the requirements.txt to leverage Docker cache
COPY requirements.txt /amazon_data/
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the current directory contents into the container at /amazon_data
COPY . /amazon_data

