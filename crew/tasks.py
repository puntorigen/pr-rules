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
    file: Optional[str] = Field(description="Affected file by rule, if applicable")
    why_is_not_complying: str = Field(description="Reason why the rule is not valid for this section, you may use markdown to highlight important keywords; only specify why it doesn't comply, without specifying what does comply")
    what_should_be_changed: Optional[List[str]] = Field(description="List of instructions for the developer on how to comply with the rule, you may use markdown to highlight important keywords")

class RulesOutput(BaseModel):
    complies: bool = Field(description="True if the rule is correct, False if the rule is not being complied")
    affected_sections: Optional[List[Reasoning]] = Field(description="If the rule doesn't comply, indicates the affected sections and the reason for non-compliance")

# task definitions
class Tasks():
    def __init__(self, PR:PRSchema, rule:str):
        self.PR = PR
        self.rule = rule
        self.pr_str = dedent(f"""\
            # PR context details:
            ## Title: {self.PR.title}
            ## Body: {self.PR.body}

            ### Files diff list of tuples: 
        """)
        for file in self.PR.files_diff:
            self.pr_str += f"filename: {str(file)}\n"
            self.pr_str += f"diff content: ```{file[1]}```\n\n"

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

                Verify the assessment of the Compliance Specialist for the rule: '{self.rule}'
            """),
            expected_output=dedent("""\
                Verified compliance status and refined assessment for given rule.
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
                # Ensure the feedback is clear, actionable, and provides value to the PR submitter.     
            """),
            output_pydantic=RulesOutput,
            expected_output=dedent("""\
                A detailed document summarizing the compliance check process, the final compliance status, and actionable feedback.
            """),
            async_execution=False,
            agent=agent
        )