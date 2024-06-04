#!/bin/sh

GITHUB_TOKEN=$1
FILE_PATH=$2
OPENAI_API_KEY=$3

if [ -z "$OPENAI_API_KEY" ]; then
  # export args as ENV variables
  export GITHUB_TOKEN=$GITHUB_TOKEN
  export FILE_PATH=$FILE_PATH  
  echo "OpenAI API key not provided. Starting Ollama using Docker Compose..."
  docker-compose up -d
  #docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
  #echo "Waiting for Ollama to be ready..."
  sleep 10
  echo "Downloading phi3 128k model..."
  docker-compose exec ollama ollama pull "phi3:3.8b-mini-128k-instruct-q8_0"
  sleep 5
  # Follow the logs of all services
  docker-compose logs -f
  #docker exec ollama ollama pull "phi3:3.8b-mini-128k-instruct-q8_0"
  # create the model file & download to local folder
  #docker exec ollama ollama create $custom_model_name -f ./Llama2ModelFile

else
  echo "OpenAI API key provided. Skipping Ollama installation."
  # only run if we have an OpenAI API key, since if not we already have the script on the docker-compose
  echo "Running the script... $@"
  python /pr_rules_check.py "$@"
fi

# Start the script
#python /pr_rules_check.py $@
#exec python /pr_rules_check.py "$@"