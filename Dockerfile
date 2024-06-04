FROM python:3.12.2-slim

# Install git and build dependencies (required for crewai[tools])
RUN apt-get update && \
    apt-get install -y git gcc g++ make curl docker.io docker-compose && \
    apt-get clean

# Install Python dependencies
RUN pip install --no-cache-dir PyGithub gitpython pydantic openai crewai[tools] 
# Install custom puntorigen crewai with latest instructor 1.3.2 (support ollama output_pydantic)
RUN pip install https://github.com/puntorigen/crewai/archive/main.zip

# Copy the action script
COPY pr_rules_check.py /pr_rules_check.py
COPY entrypoint.sh /entrypoint.sh
COPY install_ollama.sh /install_ollama.sh
RUN chmod +x /install_ollama.sh
#COPY docker-compose.yml /docker-compose.yml
RUN chmod +x /entrypoint.sh

# Copy the crew folder scripts
COPY crew /crew

# Set the entrypoint to the script
ENTRYPOINT ["/entrypoint.sh"]