#!/bin/sh

GITHUB_TOKEN=$1
FILE_PATH=$2
OPENAI_API_KEY=$3

if [ -z "$OPENAI_API_KEY" ]; then
  echo "OpenAI API key not provided. Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "OpenAI API key provided. Skipping Ollama installation."
fi
