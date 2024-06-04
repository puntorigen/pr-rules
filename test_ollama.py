import os
from crew.rule_validation import validate_rule, PRSchema

os.environ["LLM_TYPE"] = "ollama"

test = validate_rule(PRSchema(
    title = "Test PR",
    body = "Test PR body",
    files_diff = [("testfile.py","print('Hello World')")]
), "the PR description must be in english")

print(test)