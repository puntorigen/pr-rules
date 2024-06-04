#!/bin/sh

GITHUB_TOKEN=$1
FILE_PATH=$2
OPENAI_API_KEY=$3

if [ -z "$OPENAI_API_KEY" ]; then
  # export args as ENV variables
  export GITHUB_TOKEN=$GITHUB_TOKEN
  export FILE_PATH=$FILE_PATH  
  echo "OpenAI API key not provided. Starting Ollama using Shell..."
  #alternate approach
  /bin/sh -c /install_ollama.sh
else
  echo "OpenAI API key provided. Skipping Ollama installation."
  # only run if we have an OpenAI API key, since if not we already have the script on the docker-compose
fi

echo "Running the script... $@"
python /pr_rules_check.py "$@"
