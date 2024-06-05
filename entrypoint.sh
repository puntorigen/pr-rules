#!/bin/sh

GITHUB_TOKEN=$1
FILE_PATH=$2
OPENAI_API_KEY=$3
export PYTHONUNBUFFERED=1 # this is to make sure that the output is not buffered and is printed in real-time

if [ -z "$OPENAI_API_KEY" ]; then
  # export args as ENV variables
  export GITHUB_TOKEN=$GITHUB_TOKEN
  export FILE_PATH=$FILE_PATH  
  echo "OpenAI API key not provided. Starting Ollama using Shell..."
  /bin/sh -c /install_ollama.sh
else
  echo "OpenAI API key provided. Skipping Ollama installation."
fi

echo "Running the script... $@"
python -u /pr_rules_check.py "$@"
