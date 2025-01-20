from autogen import ConversableAgent

llm_config = {"model": "gpt-4o-mini"}

# 1. Define our system message, our agent's instruction
system_message = """You are a classroom lesson agent.
Given a topic, write a lesson plan for a fourth grade class.
Use the following format:
<title>Lesson plan title</title>
<learning_objectives>Key learning objectives</learning_objectives>
<script>How to introduce the topic to the kids</script>
"""

# 2. Create our purposeful agent
lesson_planner = ConversableAgent(
    name="lesson_agent",
    llm_config=llm_config,
    system_message=system_message,
)

# 3. Instruct the agent to create our lesson plan
lesson_planner.run("Today, let's introduce our kids to the solar system.")
