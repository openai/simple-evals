# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt .

# Install Python dependencies (none for now)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script and data file into the container
COPY pretty_print_csv.py .
COPY simple_qa_test_set.csv .

# Set the default command to start a Bash shell
CMD ["bash"]

