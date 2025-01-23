## Swarm

Swarms provide controllable flows between agents that are determined at the agent-level. You define hand-off, post-tool, and post-work transitions from an agent to another agent (or to end the swarm).

When designing your swarm, think about your agents in a diagram with the lines between agents being your hand-offs. Each line will have a condition statement which an LLM will evaluate. Control stays with an agent while they execute their tools and once they've finished with their tools the conditions to transition will be evaluated.

One of the unique aspects of a swarm is a shared context. ConversableAgents have a context dictionary but in a swarm that context is made common across all agents, allowing a state of the workflow to be maintained and viewed by all agents. This context can also be used within the hand off condition statements, providing more control of transitions.

AG2's swarm has a number of unique capabilities, find out more in our [Swarm documentation](https://docs.ag2.ai/docs/topics/swarm).

Here's our lesson planner workflow using AG2's Swarm.

--SNIPPET: swarm.py

```python
# TEMPORARY, THIS WILL BE REPLACED BY ABOVE SNIPPET

from autogen import SwarmAgent, initiate_swarm_chat, AfterWorkOption, ON_CONDITION, AFTER_WORK, SwarmResult

llm_config = {"model": "gpt-4o-mini", "cache_seed": None}

# 1. Context
shared_context = {
    "lesson_plans": [],
    "lesson_reviews": [],
    # Will be decremented, resulting in 0 (aka False) when no reviews are left
    "reviews_left": 2,
}

# 2. Functions
def record_plan(lesson_plan: str, context_variables: dict) -> SwarmResult:
    """Record the lesson plan"""
    context_variables["lesson_plans"].append(lesson_plan)

    # Returning the updated context so the shared context can be updated
    return SwarmResult(context_variables=context_variables)

def record_review(lesson_review: str, context_variables: dict) -> SwarmResult:
    """After a review has been made, increment the count of reviews"""
    context_variables["lesson_reviews"].append(lesson_review)
    context_variables["reviews_left"] -= 1

    # Controlling the flow to the next agent from a tool call
    return SwarmResult(
        agent=teacher if context_variables["reviews_left"] < 0 else lesson_planner,
        context_variables=context_variables
    )

planner_message = """You are a classroom lesson planner.
Given a topic, write a lesson plan for a fourth grade class.
If you are given revision feedback, update your lesson plan and record it.
Use the following format:
<title>Lesson plan title</title>
<learning_objectives>Key learning objectives</learning_objectives>
<script>How to introduce the topic to the kids</script>
"""

# 3. Our agents now have tools to use (functions above)
lesson_planner = SwarmAgent(
    name="planner_agent",
    llm_config=llm_config,
    system_message=planner_message,
    functions=[record_plan]
)

reviewer_message = """You are a classroom lesson reviewer.
You compare the lesson plan to the fourth grade curriculum
and provide a maximum of 3 recommended changes for each review.
Make sure you provide recommendations each time the plan is updated.
"""

lesson_reviewer = SwarmAgent(
    name="reviewer_agent",
    llm_config=llm_config,
    system_message=reviewer_message,
    functions=[record_review]
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

# 4. Transitions using hand-offs

# Lesson planner will create a plan and hand off to the reviewer if we're still
# allowing reviews. After that's done, transition to the teacher.
lesson_planner.register_hand_off(
    [
        ON_CONDITION(
            target=lesson_reviewer,
            condition="After creating/updating and recording the plan, it must be reviewed.",
            available="reviews_left"),
        AFTER_WORK(
            agent=teacher
        )
    ]
)

# Lesson reviewer will review the plan and return control to the planner. If they don't
# provide feedback, they'll revert back to the teacher.
lesson_reviewer.register_hand_off(
    [
        ON_CONDITION(
            target=lesson_planner,
            condition="After new feedback has been made and recorded, the plan must be updated."
        ),
        AFTER_WORK(
            agent=teacher
        )
    ]
)

# Teacher works with the lesson planner to create a plan. When control returns to them and
# a plan exists, they'll end the swarm.
teacher.register_hand_off(
    [
        ON_CONDITION(
            target=lesson_planner,
            condition="Create a lesson plan.",
            available="reviews_left"
        ),
        AFTER_WORK(AfterWorkOption.TERMINATE)
    ]
)

# 5. Run the Swarm which returns the chat and updated context variables
chat_result, context_variables, last_agent = initiate_swarm_chat(
    initial_agent=teacher,
    agents=[lesson_planner, lesson_reviewer, teacher],
    messages="Today, let's introduce our kids to the solar system.",
    context_variables=shared_context,
)

print(f"Number of reviews: {len(context_variables['lesson_reviews'])}")
print(f"Reviews remaining: {context_variables['reviews_left']}")
print(f"Final Lesson Plan:\n{context_variables['lesson_plans'][-1]}")
```
1. Our shared context, available in function calls and on agents.

2. Functions that represent the work the agents carry out, these the update shared context and, optionally, managed transitions.

3. Agents setup with their tools, `functions`, and a system message and LLM configuration.

4. The important hand-offs, defining the conditions for which to transfer to other agents and what to do after their work is finished (equivalent to no longer calling tools). Transfer conditions can be turned on/off using the `available` parameter.

5. Kick off the swarm with our agents and shared context. Similar to `initiate_chat`, `initiate_swarm_chat` returns the chat result (messages and summary) and the final shared context.

```console
Number of reviews: 2
Reviews remaining: 0
Final Lesson Plan:
<title>Exploring the Solar System</title>
<learning_objectives>Students will be able to identify and describe the planets in the Solar System, understand the concept of orbits, and recognize the sun as the center of our Solar System.</learning_objectives>
<script>Using a large poster of the Solar System, I will introduce the planets one by one, discussing key characteristics such as size, color, and distance from the sun. I will engage the students by asking questions about their favorite planets and what they know about them. We will do a quick demo using a simple model to show how planets orbit around the sun. Students will create their own solar system models in small groups with various materials to understand the scale and distance better, fostering teamwork. We will incorporate a multimedia presentation to visualize the orbits and relative sizes of the planets. Finally, a short assessment will be conducted at the end of the lesson to gauge students' understanding, using quizzes or presentations of their models.</script>
```

Next > tools.md
