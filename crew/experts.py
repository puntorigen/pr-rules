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
            goal='Oversees compliance checks and delegates to specialized experts if needed, always paying special focus to the defined rule, ignoring other comments that are not related to the specified rule.',
            tools=[],
            backstory=dedent("""\
                A meticulous professional with deep knowledge of coding standards 
                and best practices, capable of identifying nuances in compliance about the requested rule."""),
            allow_delegation=True, # can delegate tasks to specialized experts
            #verbose=True
        )

    def specialized_experts(self):
        # dict with array of specialized experts (python,java,database,security,etc.)
        return {
            "coding": [
                Agent(
                    role='Python Expert',
                    goal='Provides opinions on Python-specific code regarding the requested rule.',
                    tools=[
                        #add python knowledge from somewhere
                        #RagTool.add('https://www.python.org/')
                        #RagTool.add('')
                    ],
                    backstory=dedent("""\
                        A Python expert with a deep understanding of Python-specific language terminology and 
                        best practices, capable of providing detailed feedback on Python code, focused on the requested rule we are checking.
                    """),
                    allow_delegation=True,
                    #verbose=True
                )
            ],
            "database": [
                Agent(
                    role='SQL Expert',
                    goal='Provides opinions on SQL database-specific code regarding the requested rule.',
                    tools=[
                        #add python knowledge from somewhere
                        #RagTool.add('https://www.python.org/')
                        #RagTool.add('')
                    ],
                    backstory=dedent("""\
                        A SQL expert with a deep understanding of SQL-specific language terminology, syntax and
                        best practices, capable of providing detailed feedback on SQL, focused on the requested rule we are checking.
                    """),
                    allow_delegation=False,
                    #verbose=True
                )
            ]
        }

    def review_agent(self):
        return Agent(
            role='Review Agent',
            #goal='Verifies the accuracy of the Compliance Specialist’s assessment, consulting with specialized experts if needed, always in regards to the requested rule and nothing else.',
            goal='Verifies the accuracy of the Compliance Specialist’s assessment, always in regards to the requested rule and nothing else.',
            tools=[],
            backstory=dedent("""\
                An experienced reviewer with a background in code review and 
                quality assurance, ensuring that compliance checks are correctly applied for the requested rule."""),
            #verbose=True,
            allow_delegation=False # Reviewer can delegate tasks to specialized experts
        )

    def feedback_agent(self):
        return Agent(
            role='Feedback Agent',
            goal='Generates a detailed feedback report based on the assessments for the specified rule. You query info to specialized experts if needed, always in regards to the requested rule and nothing else, for writting a better report.',
            tools=[],
            backstory=dedent("""\
                A communication expert who translates technical assessments into clear, 
                actionable feedback, that is easily understood by junior engineers.
            """),
            allow_delegation=True,
            #verbose=True
        )
