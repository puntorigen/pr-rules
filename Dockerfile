FROM python:3.12.2-slim

# Install git and build dependencies (required for crewai[tools])
RUN apt-get update && \
    apt-get install -y git gcc g++ make curl docker.io && \
    apt-get clean

# Install Python dependencies
RUN pip install --no-cache-dir PyGithub gitpython pydantic openai crewai crewai[tools]

# Copy the action script
COPY pr_rules_check.py /pr_rules_check.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy the crew folder scripts
COPY crew /crew

# Set the entrypoint to the script
ENTRYPOINT ["/bin/sh", "-c", "/entrypoint.sh \"$@\""]
#ENTRYPOINT ["/entrypoint.sh"]
#ENTRYPOINT ["/bin/sh", "-c", "/install_ollama.sh \"$0\" \"$1\" \"$2\" && python /pr_rules_check.py \"$0\" \"$1\" \"$2\""]
#ENTRYPOINT ["python", "/pr_rules_check.py"]
