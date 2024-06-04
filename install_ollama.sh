#!/bin/sh

GITHUB_TOKEN=$1
FILE_PATH=$2
OPENAI_API_KEY=$3

if [ -z "$OPENAI_API_KEY" ]; then
  echo "OpenAI API key not provided. Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
  sleep 10
  echo "Downloading Ollama model... phi3:3.8b-mini-128k-instruct-q8_0"
  ollama pull phi3:3.8b-mini-128k-instruct-q8_0
  sleep 5
  echo "Starting Ollama server ..."
  ollama serve &
else
  echo "OpenAI API key provided. Skipping Ollama installation."
fi
