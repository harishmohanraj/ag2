from autogen import AFTER_WORK, ON_CONDITION, AfterWorkOption, SwarmAgent, SwarmResult, initiate_swarm_chat

llm_config = {"model": "gpt-4o-mini", "cache_seed": None}

# Context

shared_context = {
    "lesson_plans": [],
    "lesson_reviews": [],
    "reviews_left": 2,
}


# Functions
def record_plan(lesson_plan: str, context_variables: dict) -> SwarmResult:
    """Record the lesson plan"""
    context_variables["lesson_plans"].append(lesson_plan)
    return SwarmResult(context_variables=context_variables)


def record_review(lesson_review: str, context_variables: dict) -> SwarmResult:
    """After a review has been made, increment the count of reviews"""
    context_variables["lesson_reviews"].append(lesson_review)
    context_variables["reviews_left"] -= 1
    return SwarmResult(
        agent=teacher if context_variables["reviews_left"] < 0 else lesson_planner, context_variables=context_variables
    )


# 1. Our agents are setup with just a system message and LLM
planner_message = """You are a classroom lesson planner.
Given a topic, write a lesson plan for a fourth grade class.
If you are given revision feedback, update your lesson plan and record it.
Use the following format:
<title>Lesson plan title</title>
<learning_objectives>Key learning objectives</learning_objectives>
<script>How to introduce the topic to the kids</script>
"""

lesson_planner = SwarmAgent(
    name="planner_agent", llm_config=llm_config, system_message=planner_message, functions=[record_plan]
)

reviewer_message = """You are a classroom lesson reviewer.
You compare the lesson plan to the fourth grade curriculum
and provide a maximum of 3 recommended changes for each review.
Make sure you provide recommendations each time the plan is updated.
"""

lesson_reviewer = SwarmAgent(
    name="reviewer_agent", llm_config=llm_config, system_message=reviewer_message, functions=[record_review]
)

teacher_message = """You are a classroom teacher.
You decide topics for lessons and work with a lesson planner.
and reviewer to create and finalise lesson plans.
"""

teacher = SwarmAgent(
    name="teacher_agent",
    llm_config=llm_config,
    system_message=teacher_message,
)


# Helper functions

# Transitions using hand-offs

# Lesson planner will create a plan and hand off to the reviewer if we're still allowing reviews,
# otherwise transition to the teacher
lesson_planner.register_hand_off(
    [
        ON_CONDITION(
            target=lesson_reviewer,
            condition="After creating/updating and recording the plan, it must be reviewed.",
            available="reviews_left",
        ),
        AFTER_WORK(agent=teacher),
    ]
)

# Lesson reviewer will review the plan and return control to the planner if there's no plan to review, otherwise it will
# provide a review and
lesson_reviewer.register_hand_off(
    [
        ON_CONDITION(
            target=lesson_planner, condition="After new feedback has been made and recorded, the plan must be updated."
        ),
        AFTER_WORK(agent=teacher),
    ]
)

teacher.register_hand_off(
    [
        ON_CONDITION(target=lesson_planner, condition="Create a lesson plan.", available="reviews_left"),
        AFTER_WORK(AfterWorkOption.TERMINATE),
    ]
)

chat_result, context_variables, last_agent = initiate_swarm_chat(
    initial_agent=teacher,
    agents=[lesson_planner, lesson_reviewer, teacher],
    messages="Today, let's introduce our kids to the solar system.",
    context_variables=shared_context,
)
print(context_variables["reviews_left"])
print(len(context_variables["lesson_reviews"]))
print(context_variables["lesson_reviews"][-1])
print(len(context_variables["lesson_plans"]))
print(context_variables["lesson_plans"][-1])
