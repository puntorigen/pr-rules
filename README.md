# pr-rules
Github Action for checking a given PR against a markdown file with checklist rules written in natural language (they can be written on any language).

# Requirements
- OpenAI API Key

# Same usage
On the root of your repo, create a file called pr-rules.md with the following contents:

```md
[] all code variables must use snake_case convention
[] the PR description must specify which tests where performed
[] no code diff should be more than 100 lines 
```

then on your repo create a github workflow template like the following:

```yml
name: PR BOT

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  test-action:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Run PR BOT
        uses: puntorigen/pr-rules@v1.0.0
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          openai-apikey: 'your-api-key'
          file-path: 'pr-rules.md'

```

Now everytime you create a PR on your repo, the action will check it complies to the rules specified on the markdown and write a comment with them checked if succesful or not. If not valid, below the item there'll be an explanation.