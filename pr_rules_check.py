import os
import sys
import re
from typing import List, Optional, Literal
from github import Github
from openai import OpenAI
from pydantic import BaseModel, Field
import instructor

# Define Pydantic models for structured output
class Reasoning(BaseModel):
    section: Literal["title", "description", "file", "other"] = Field(description="Section of the PR that is not complying (title, description, file, or other)")
    file: Optional[str] = Field(description="Affected file by rule, if applicable")
    why_is_not_complying: str = Field(description="Reason why the rule is not valid for this section")
    what_should_be_changed: List[str] = Field(description="List of instructions for the developer on how to comply with the rule")

class RulesOutput(BaseModel):
    complies: bool = Field(description="True if the rule is correct, False if the rule is not being complied")
    affected_sections: Optional[List[Reasoning]] = Field(description="If the rule doesn't comply, indicates the affected sections and the reason for non-compliance")

def initialize_instructor(api_key: str):
    return instructor.from_openai(OpenAI(api_key=api_key))

def read_markdown_file(repo, branch, file_path):
    try:
        file_content = repo.get_contents(file_path, ref=branch)
        return file_content.decoded_content.decode('utf-8')
    except Exception as e:
        print(f"Error reading markdown file: {e}")
        return None

def parse_checklist_items(content):
    checklist_pattern = re.compile(r'\[\]\s+(.*)')
    checklist_items = checklist_pattern.findall(content)
    return checklist_items

def get_diff(repo, base_branch, compare_branch):
    try:
        comparison = repo.compare(base_branch, compare_branch)
        diffs = []
        for file in comparison.files:
            if file.patch:
                diffs.append(f"Filename: {file.filename}\nDiff:\n{file.patch}\n")
        return "\n".join(diffs)
    except Exception as e:
        print(f"Error getting diff: {e}")
        return None

def build_llm_prompt(pr_title, pr_body, diff, rule):
    prompt = f"PR Title: {pr_title}\n\nPR Description: {pr_body}\n\n"
    if diff:
        prompt += f"Modified Files and Changes:\n{diff}\n\n"
    prompt += f"Rule to Check:\n{rule}\n\n"
    prompt += "Check the above rule based on the PR title, description, and modified files. If the rule fails, provide a reason for the failure."
    return prompt

def get_llm_response(client, prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        response_model=RulesOutput,
        messages=[
            {"role": "system", "content": "# You are an expert PR analyst who has been given the task to check the current PR given context against a given rule. If the rule doesn't apply, return the reasoning and an easy to understand but detailed explanation of why it doesn't, so the developer can fix the PR to comply with the rule."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        stream=False
    )
    return response

def post_comment(pr, comment_body):
    try:
        pr.create_issue_comment(body=comment_body)
        print("Comment posted on the PR.")
    except Exception as e:
        print(f"Error posting comment: {e}")

def main():
    # Get inputs
    token = sys.argv[1]
    openai_api_key = sys.argv[2]
    rules_file_path = sys.argv[3]

    # GitHub repository details from environment variables
    repository = os.getenv('GITHUB_REPOSITORY')
    ref = os.getenv('GITHUB_REF')
    pull_number = ref.split('/')[-2]
    owner, repo_name = repository.split('/')

    # Initialize GitHub API
    g = Github(token)
    repo = g.get_repo(f"{owner}/{repo_name}")

    # Initialize Instructor client
    client_instructor = initialize_instructor(openai_api_key)

    # Get the pull request details
    pr = repo.get_pull(int(pull_number))
    base_branch = pr.base.ref
    compare_branch = pr.head.ref

    # Read rules from markdown file
    rules_content = read_markdown_file(repo, base_branch, rules_file_path)
    if rules_content is None:
        print("Failed to read the rules file. Exiting.")
        return

    checklist_items = parse_checklist_items(rules_content)

    # Get the diff of the modified files between the base branch and the compare branch
    print(f"Getting diff between {base_branch} and {compare_branch}...")
    diff = get_diff(repo, base_branch, compare_branch)

    # Build comment content
    comment_content = "# PR Rules Checklist\n\n"
    processed_items_count = 0
    for item in checklist_items:
        prompt = build_llm_prompt(pr.title, pr.body, diff, item)
        print(f"LLM Prompt built for rule: {item}")

        llm_response = get_llm_response(client_instructor, prompt)
        print(f"LLM Response received for rule: {item}")

        if llm_response.complies:
            comment_content += f"- [x] $\color{{ForestGreen}}{{{item}}}$\n"
        else:
            comment_content += f"- [x] $\color{{Red}}{{{item}}}$\n"
            comment_content += "  - **Reason for failure:**\n"
            for reasoning in llm_response.affected_sections or []:
                comment_content += f"    - **Affected Section:** {reasoning.section}\n"
                if reasoning.file:
                    comment_content += f"    - **Affected File:** {reasoning.file}\n"
                comment_content += f"    - **Reason:** {reasoning.why_is_not_complying}\n"
                comment_content += "    - **Suggested Changes:**\n"
                for change in reasoning.what_should_be_changed:
                    comment_content += f"      - {change}\n"
            break  # Stop processing further rules on failure
        processed_items_count += 1

    # Add remaining unchecked items
    remaining_items = checklist_items[processed_items_count:]
    for item in remaining_items:
        comment_content += f"- [ ] {item}\n"

    # Post the comment on the PR
    post_comment(pr, comment_content)

if __name__ == "__main__":
    main()
