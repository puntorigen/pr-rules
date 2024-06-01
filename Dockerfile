FROM python:3.9-slim

# Install git
RUN apt-get update && apt-get install -y git

# Install Python dependencies
RUN pip install --no-cache-dir PyGithub gitpython pydantic instructor openai

# Copy the action script
COPY pr_rules_check.py /pr_rules_check.py

# Set the entrypoint to the script
ENTRYPOINT ["python", "/pr_rules_check.py"]
