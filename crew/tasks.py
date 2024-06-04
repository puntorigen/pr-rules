from dataclasses import dataclass, field
from textwrap import dedent
from crewai import Task
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Tuple

@dataclass
class PRSchema:
    title: str
    body: str
    files_diff: List[Tuple[str, str]] = field(default_factory=list)

    def __str__(self):
        files_diff_str = ', '.join([f'({file[0]}, {file[1]})' for file in self.files_diff])
        return f"PRSchema(title={self.title}, body={self.body}, files_diff=[{files_diff_str}])"

# output schema definitions
class RuleValidity(BaseModel):
    is_relevant: bool = Field(description="A boolean value indicating whether the rule is relevant to the PR contents.")

class Reasoning(BaseModel):
    section: Literal["title", "description", "file", "other"] = Field(description="Section of the PR that is not complying (title, description, file, or other)")
    file: Optional[str] = Field(description="Affected filename by rule, if applicable")
    why_is_not_complying: str = Field(description="Reason why the rule is not valid for this section, you may use markdown to highlight important keywords; only specify why it doesn't comply, without specifying what does comply, and don't repeat the rule on the reasoning.")
    what_should_be_changed: Optional[List[str]] = Field(description="List of instructions for the developer on how to comply with the rule, using best practices regarding the specified rule only and no other recommendations not related to the rule. Provide an example of a valid way to comply with the rule, wrapping it on a markdown code-block. You may use markdown syntax for bold syntax and markdown code-blocks for examples.")
    #example_fix: List[str] = Field(description="Upto two examples on how the section should be fixed to comply with the rule, so a junior engineer understands how to fix it")

class RulesOutput(BaseModel):
    complies: bool = Field(description="True if the rule is correct, False if the rule is not being complied")
    score: int = Field(description="Score of the adherence to the rule, from 0 (bad) to 100 (perfect)")
    affected_sections: Optional[List[Reasoning]] = Field(description="If the PR doesn't adhere to the rule, indicates the affected sections and the reason for non-compliance regarding only the specified rule.")
 
# task definitions
class Tasks():
    def __init__(self, PR:PRSchema, rule:str):
        self.PR = PR
        self.rule = rule
        self.pr_str = dedent(f"""\
            # PR context details:
            ## Title: "{self.PR.title}"
            ## Body: "{self.PR.body}"

            ### Files diff list of tuples: 
        """)
        for file in self.PR.files_diff:
            self.pr_str += f"filename:\n{str(file[0])}\n"
            self.pr_str += f"diff content:\n```{file[1]}```\n"

    def is_rule_relevant(self, agent):
        return Task(
            description=dedent(f"""\
                {self.pr_str}

                # Analyze the PR to determine if the rule is relevant to the PR contents.
                # The rule to be analyzed is:
                '{self.rule}'
            """),
            output_pydantic=RuleValidity,
            expected_output=dedent("""\
                A boolean value indicating whether the rule is relevant to the given PR contents."""),
            async_execution=False,
            agent=agent
        )

    def check_complaince(self, agent):
        return Task(
            description=dedent(f"""\
                {self.pr_str}

                # Check the PR for compliance with the following rule: '{self.rule}'
            """),
            output_pydantic=RulesOutput,
            expected_output=dedent("""\
                Compliance status (complies/does not comply) and detailed assessment.
            """),
            async_execution=False,
            agent=agent
        )
    
    def verify_assessment(self, agent, compliance_result):
        return Task(
            context=[compliance_result],
            description=dedent(f"""\
                {self.pr_str}

                Verify the assessment of the Compliance Specialist only for the rule: '{self.rule}'
            """),
            expected_output=dedent("""\
                Verified compliance status and refined assessment only for the given rule regarding the PR and nothing else.
            """),
            async_execution=False,
            agent=agent
        )

    def generate_feedback(self, agent, verified_compliance):
        return Task(
            context=[verified_compliance],
            description=dedent(f"""\
                {self.pr_str}

                # Compile the verified assessments into a comprehensive feedback report.
                # Never change the given rule validation from the previous agents.
                # Ensure the feedback is clear, actionable, and provides value to the PR submitter in specific regards to how the rule '{self.rule}' doesn't comply and nothing else.
                # It's critical that your output is focused only on the requested rule and nothing else.     
            """),
            output_pydantic=RulesOutput,
            #output_file="feedback_report.md",
            expected_output=dedent(f"""\
                A detailed document summarizing the compliance check process for the given rule of '{self.rule}', which files are related, the final compliance status, with actionable feedback that a junior engineer can easily understand and apply, with an example fix or hint.
                Never change the given rule assestment from the previous agents, even if it can be improved. If it's valid, it's valid, if not, it isn't, but never say that even if it's valid it should be different.
            """),
            async_execution=False,
            agent=agent
        )