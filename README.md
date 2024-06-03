# PR Rules

A GitHub Action for checking pull requests (PRs) against a markdown file containing checklist rules written in natural language. It uses a team of experts to assess and validate your repository's rules.

## Requirements

- OpenAI API Key

## Sample Usage

1. In the root of your repository, create a file called `pr-rules.md` with the following contents:

    ```md
    - [x] All code variables must use snake_case convention.
    - [ ] The PR description cannot be empty.
    - [x] The PR description must be in English.
    - [x] Method names should always be descriptive.
    - [x] The code can't contain literal SQL statements.
    - [ ] No code diff should be more than 100 lines.
    ```

    - All task list items checked with an `x` are mandatory and will cause the action to fail if not complied with.
    - Unchecked items will issue a warning of non-compliance but will not cause the action to fail.

2. Create a GitHub workflow template in your repository like the following:

    ```yml
    name: PR BOT

    on:
      pull_request:
        types: [opened, synchronize, reopened]

    # This is needed for the action to be able to post comments
    permissions:
      issues: write
      pull-requests: write
      contents: read

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
              openai-api-key: ${{ secrets.OPENAI_API_KEY }}
              file-path: 'pr-rules.md'
    ```

Now, every time you create a PR in your repository, the action will check if it complies with the rules specified in the markdown file. It will then post a comment with the results, indicating whether the PR is successful or not. If the PR is not valid, an explanation will be provided below the non-compliant items.

## Example Comment by BOT

![Example Comment](./example.png)
