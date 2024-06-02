# Defines a 'Team of Experts & Tasks' for validating a given PR against a given rule
from crewai import Crew
from crew.experts import Experts
from crew.tasks import Tasks, PRSchema, RulesOutput

def validate_rule(PR: PRSchema, rule: str):
    # Define the team
    expert = Experts()
    rule_validator = expert.rule_relevant_analyst()
    compliance_specialist = expert.compliance_specialist()
    specialized_experts = expert.specialized_experts()
    review_agent = expert.review_agent()
    feedback_agent = expert.feedback_agent()

    # Define the tasks
    my_tasks = Tasks(PR, rule)
    is_rule_relevant = my_tasks.is_rule_relevant(rule_validator)

    # kick off the first task to see if we need to prceed with the rest of the tasks
    test_crew = Crew(
        agents=[rule_validator],
        tasks=[is_rule_relevant]
    )
    print("Starting Validation Crew")
    is_valid = test_crew.kickoff()
    print("output from initial validation task",is_valid)

    if is_valid.is_relevant == False:
        print("Rule is not relevant to the PR context")
        return RulesOutput(complies=True)
        #return { "is_relevant": False } # Rule is not relevant to the PR

    print("Rule seems valid for PR context, proceeding with the rest of the tasks")
    # define the rest of the tasks
    check_compliance = my_tasks.check_complaince(compliance_specialist)
    verify_assessment = my_tasks.verify_assessment(review_agent, check_compliance)
    generate_feedback = my_tasks.generate_feedback(feedback_agent, verify_assessment)

    # Define the final evaluation crew
    print("executing review crew for rule: "+rule)
    crew = Crew(
        agents=[ # include available specialiazied experts here as well
            compliance_specialist, *specialized_experts["coding"],
            review_agent, feedback_agent
        ], 
        tasks=[
            check_compliance, verify_assessment, generate_feedback
        ]
    )
    return crew.kickoff()
