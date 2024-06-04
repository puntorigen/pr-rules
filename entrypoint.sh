#!/bin/sh

GITHUB_TOKEN=$1
FILE_PATH=$2
OPENAI_API_KEY=$3

if [ -z "$OPENAI_API_KEY" ]; then
  echo "OpenAI API key not provided. Starting Ollama..."
  docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
  echo "Waiting for Ollama to be ready..."
  sleep 10
  echo "Downloading phi3 128k model..."
  docker exec ollama ollama pull "phi3:3.8b-mini-128k-instruct-q8_0"
else
  echo "OpenAI API key provided. Skipping Ollama installation."
fi

# Start the script
python /pr_rules_check.py "$@"