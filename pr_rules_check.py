import os, sys, re
from github import Github
from crew.rule_validation import validate_rule, PRSchema
from dataclasses import dataclass, field

@dataclass
class CheckListItem:
    text: str
    type: str

def read_markdown_file(repo, branch, file_path):
    try:
        file_content = repo.get_contents(file_path, ref=branch)
        return file_content.decoded_content.decode('utf-8')
    except Exception as e:
        print(f"Error reading markdown file: {e}")
        return None

def parse_checklist_items(content) -> list[CheckListItem]:
    # Update the regex pattern to match both '- [x] ' and '- [ ] ' at the beginning of each line
    checklist_pattern = re.compile(r'- \[([ xX])\] (.*)')
    checklist_items = []

    for line in content.split('\n'):
        match = checklist_pattern.match(line)
        if match:
            status, item = match.groups()
            item_data = CheckListItem(
                text=item.strip(),
                type='mandatory' if status.lower() == 'x' else 'warning'
            )
            checklist_items.append(item_data)

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

def animated_rule(type="success",rule="",score=100,speed=3000):
    escaped_text = rule.replace(" ",r"+")
    if type == "success":
        return f"[![{rule}](https://readme-typing-svg.demolab.com?font=Fira+Code&size=12&duration={speed}&pause=1000&color=00B60A&random=false&repeat=false&width=550&height=18&lines=-+%E2%9C%85+{escaped_text}+(score+{score}%2F100))](https://github.com/puntorigen/pr-rules)"
    if type == "pending":
        return f"[![{rule}](https://readme-typing-svg.demolab.com?font=Fira+Code&size=12&duration={speed}&pause=1000&color=97AEB8&random=false&repeat=false&width=550&height=18&lines=-+%F0%9F%95%92+{escaped_text})](https://github.com/puntorigen/pr-rules)"
    if type == "warning":
        return f"[![{rule}](https://readme-typing-svg.demolab.com?font=Fira+Code&size=12&duration={speed}&pause=1500&color=FF5F15&repeat=true&random=false&width=550&height=18&lines=-+%E2%9D%8C+{escaped_text}+(score+{score}%2F100))](https://github.com/puntorigen/pr-rules)"
    return f"[![{rule}](https://readme-typing-svg.demolab.com?font=Fira+Code&size=12&duration={speed}&pause=1500&color=FF0000&repeat=true&random=false&width=550&height=18&lines=-+%E2%9D%8C+{escaped_text}+(score+{score}%2F100))](https://github.com/puntorigen/pr-rules)"

def main():
    # test inputs source
    rules_file_path = os.getenv('FILE_PATH')
    # Get inputs from args if rules_file_path is not set
    if not rules_file_path:
        token = sys.argv[1]
        rules_file_path = sys.argv[2]
        openai_api_key = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        # get from environment variables
        token = os.getenv('GITHUB_TOKEN')
        openai_api_key = os.getenv('OPENAI_API_KEY')

    # set OpenAI api key or install & use Ollama
    if openai_api_key:
        os.environ["LLM_TYPE"] = "openai"
        os.environ["OPENAI_API_KEY"] = openai_api_key
        os.environ["OPENAI_MODEL_NAME"] = "gpt-4" # the best model for these tasks
    else:
        os.environ["LLM_TYPE"] = "ollama"
        os.environ["OPENAI_API_BASE"] = "http://127.0.0.1:11434" # Ollama API base URL; use docker instance name inside actions
        os.environ["OPENAI_API_KEY"] = "ollama"
        #os.environ["OPENAI_MODEL_NAME"] = "phi3:3.8b-mini-128k-instruct-q8_0"

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
    comment_content = "# PR Rules Checklist\n"
    if not openai_api_key:
        comment_content += "(ollama version)\n\n"
    comment_content += "\n"

    processed_items_count = 0
    for rule in checklist_items:
        print(f"------------------------------")
        print(f"Checking rule: {rule.text}")

        llm_response = validate_rule(PRSchema(
            title = pr.title,
            body = pr.body,
            files_diff = diff
        ), rule.text)

        print(f"LLM Crew Response received for rule: {rule.text}", llm_response)

        if llm_response.complies:
            #comment_content += f"- ✅ {color_text(rule, 'ForestGreen')} (score: {llm_response.score}/100)\n"
            comment_content += animated_rule("success",rule.text,llm_response.score,3000+(processed_items_count*500))
        else:
            #comment_content += f"- ❌ {color_text(rule, 'Red')} (score: {llm_response.score}/100)\n"
            if rule.type == 'mandatory':
                comment_content += animated_rule("failure",rule.text,llm_response.score,3000+(processed_items_count*500))
                comment_content += "\n- **Reason for failure:**\n"
            else:
                comment_content += animated_rule("warning",rule.text,llm_response.score,3000+(processed_items_count*500))
                comment_content += "\n- **Reason for warning:**\n"
            for reasoning in llm_response.affected_sections or []:
                if reasoning.file:
                    comment_content += f"  - **Affected File:** {reasoning.file}\n"
                else:
                    comment_content += f"  - **Affected Section:** {reasoning.section}\n"
                comment_content += f"  - **Reason:** {reasoning.why_is_not_complying}\n"
                if reasoning.what_should_be_changed:
                    comment_content += "  - **Suggested Changes:**\n"
                    for change in reasoning.what_should_be_changed:
                        comment_content += f"    - {change}\n"
                #if reasoning.example_fix:
                #    comment_content += f"  - **Example Code Improvements:**\n"
                #    for fix in reasoning.example_fix:
                #        comment_content += f"    - {fix}\n"
            # Stop processing further rules on failure, only if rule.type is mandatory
            if rule.type == 'mandatory':
                break  
        processed_items_count += 1

    # Add remaining unchecked items
    remaining_items = checklist_items[processed_items_count+1:]
    comment_content += "\n"
    for rule in remaining_items:
        comment_content += animated_rule("pending",rule.text,100,3000) + "\n"
        #comment_content += f"- [ ] {rule}\n" 

    # Post the comment on the PR
    post_comment(pr, comment_content)

    # Fail the action if we have any remaining rules to check and we are not ollama
    if remaining_items and openai_api_key:
        sys.exit(1)
    #if not llm_response.complies:

if __name__ == "__main__":
    main()
