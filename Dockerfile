FROM python:3.9-slim

# Install dependencies
RUN pip install PyGithub gitpython github git pydantic instructor

# Copy the action script
COPY pr_rules_check.py /pr_rules_check.py

# Set the entrypoint to the script
ENTRYPOINT ["python", "/pr_rules_check.py"]
