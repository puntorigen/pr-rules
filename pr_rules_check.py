import os, sys, re
from github import Github
from openai import OpenAI
from crew.rule_validation import validate_rule, PRSchema

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
    # return as a list of tuples
    try:
        comparison = repo.compare(base_branch, compare_branch)
        diffs = []
        for file in comparison.files:
            if file.patch:
                diffs.append((file.filename, file.patch))
                #diffs.append(f"Filename: {file.filename}\nDiff:\n{file.patch}\n")
        #return "\n".join(diffs)
        return diffs
    except Exception as e:
        print(f"Error getting diff: {e}")
        return None

def post_comment(pr, comment_body):
    try:
        pr.create_issue_comment(body=comment_body)
        print("Comment posted on the PR.")
    except Exception as e:
        print(f"Error posting comment: {e}")

def escape_text(text):
    # Enclose spaces and underscores in braces
    escaped_text = text.replace(" ", r"\ ").replace("_", r"\_")
    return escaped_text

def color_text(text, color):
    return f"$\\color{{{color}}}{{{escape_text(text)}}}$"

def main():
    # Get inputs
    token = sys.argv[1]
    openai_api_key = sys.argv[2]
    rules_file_path = sys.argv[3]

    # set openai api key on env
    os.environ["OPENAI_API_KEY"] = openai_api_key

    # GitHub repository details from environment variables
    repository = os.getenv('GITHUB_REPOSITORY')
    ref = os.getenv('GITHUB_REF')
    pull_number = ref.split('/')[-2]
    owner, repo_name = repository.split('/')

    # Initialize GitHub API
    g = Github(token)
    repo = g.get_repo(f"{owner}/{repo_name}")

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
    for rule in checklist_items:
        print(f"Checking rule: {rule}")

        llm_response = validate_rule(PRSchema(
            title = pr.title,
            body = pr.body,
            files_diff = diff
        ), rule)

        print(f"LLM Crew Response received for rule: {rule}", llm_response)

        if llm_response.complies:
            comment_content += f"- ✅ {color_text(rule, 'ForestGreen')}\n"
        else:
            comment_content += f"- ❌ {color_text(rule, 'Red')}\n"
            comment_content += "  - **Reason for failure:**\n"
            for reasoning in llm_response.affected_sections or []:
                if reasoning.file:
                    comment_content += f"    - **Affected File:** {reasoning.file}\n"
                else:
                    comment_content += f"    - **Affected Section:** {reasoning.section}\n"
                comment_content += f"    - **Reason:** {reasoning.why_is_not_complying}\n"
                if reasoning.what_should_be_changed:
                    comment_content += "    - **Suggested Changes:**\n"
                    for change in reasoning.what_should_be_changed:
                        comment_content += f"      - {change}\n"
                if reasoning.example_fix:
                    comment_content += f"    - **Example Fix:**\n"
                    comment_content += f"      - {reasoning.reasoning.example_fix}\n"
            break  # Stop processing further rules on failure
        processed_items_count += 1

    # Add remaining unchecked items
    remaining_items = checklist_items[processed_items_count+1:]
    for item in remaining_items:
        comment_content += f"- [ ] {item}\n"

    # Post the comment on the PR
    post_comment(pr, comment_content)

    # Fail the action if any rule check failed
    if not llm_response.complies:
        sys.exit(1)

if __name__ == "__main__":
    main()
