FROM python:3.12.2-slim

# Install git
RUN apt-get update && apt-get install -y git

# Install Python dependencies
RUN pip install --no-cache-dir PyGithub gitpython pydantic openai crewai crewai[tools]

# Copy the action script
COPY pr_rules_check.py /pr_rules_check.py

# Copy the crew folder scripts
COPY crew /crew

# Set the entrypoint to the script
ENTRYPOINT ["python", "/pr_rules_check.py"]
