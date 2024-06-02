from textwrap import dedent
from crewai import Agent

# Assuming ExaSearchTool is a placeholder for actual tools that agents can use
#from tools import ResearchTools, FeedbackTools
from crewai_tools import RagTool

class Experts():
    def rule_relevant_analyst(self):
        return Agent(
            role='Rule Relevance Analyst',
            goal='Determines if a rule is related to the PR',
            #tools=ResearchTools.tools(),
            backstory=dedent("""\
                An expert in understanding both high-level requirements and 
                intricate details of code changes, ensuring rules are relevant 
                to PR contents."""),
            verbose=True,
            allow_delegation=False
        )

    def compliance_specialist(self):
        return Agent(
            role='Compliance Specialist',
            goal='Oversees compliance checks and delegates to specialized experts if needed.',
            tools=[],
            backstory=dedent("""\
                A meticulous professional with deep knowledge of coding standards 
                and best practices, capable of identifying nuances in compliance."""),
            allow_delegation=True, # can delegate tasks to specialized experts
            verbose=True
        )

    def specialized_experts(self):
        # dict with array of specialized experts (python,java,database,security,etc.)
        return {
            "coding": [
                Agent(
                    role='Python Expert',
                    goal='Provides opinions on Python-specific rules.',
                    tools=[
                        #add python knowledge from somewhere
                        #RagTool.add('https://www.python.org/')
                        #RagTool.add('')
                    ],
                    backstory=dedent("""\
                        A Python expert with a deep understanding of Python-specific rules
                    """),
                    allow_delegation=True,
                    verbose=True
                )
            ]
        }

    def review_agent(self):
        return Agent(
            role='Review Agent',
            goal='Verifies the accuracy of the Compliance Specialist’s assessment, consulting with specialized experts if needed.',
            tools=[],
            backstory=dedent("""\
                An experienced reviewer with a background in code review and 
                quality assurance, ensuring that compliance checks are correctly applied."""),
            verbose=True,
            allow_delegation=True # Reviewer can delegate tasks to specialized experts
        )

    def feedback_agent(self):
        return Agent(
            role='Feedback Agent',
            goal='Generates a detailed feedback report based on the assessments.',
            tools=[],
            backstory=dedent("""\
                A communication expert who translates technical assessments 
                into clear, actionable feedback."""),
            verbose=True
        )
