FROM python:3.9-slim

# Install dependencies
RUN pip install PyGithub gitpython

# Copy the action script
COPY pr_bot.py /pr_bot.py

# Set the entrypoint to the script
ENTRYPOINT ["python", "/pr_bot.py"]
