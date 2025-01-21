In this guide, you'll learn how to create AG2 agents and get them to work together.

## Before we get started...

### GitHub Codespaces

The fastest way to get started is to open the code snippets in GitHub Codespaces and start playing with the code yourself. Each snippet has a button that will open it in a fully functioning AG2 Codespace.

Add an OPENAI_API_KEY secret to your GitHub Codespaces so your agents can use an LLM. See the [instructions here](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces).

### Installing AG2

Alternatively, if you'd like to install AG2 on your machine:

```bash
pip install ag2
```

:::note
We recommended using a virtual environment
:::

### LLM configurations

AG2 agents can use LLMs through providers such as OpenAI, Anthropic, Google, Amazon, Mistral AI, Cerebras, and Groq. Locally hosted models can also be used through Ollama, LiteLLM, and LM Studio.

The examples include an LLM configuration for OpenAI's `GPT-4o mini` model. Set your `OPENAI_API_KEY` environment variable accordingly:

macOS / Linux
```bash
export OPENAI_API_KEY="your_api_key_here"
```

 Windows
 ```bash
setx OPENAI_API_KEY "your_api_key_here"
 ```

If you would like to use a different provider, [see how here](https://docs.ag2.ai/docs/topics/non-openai-models/about-using-nonopenai-models).


# Say hello to ConversableAgent

ConversableAgent is at the heart of all AG2 agents while also being a fully functioning agent.

Let's *converse* with ConversableAgent in just 4 simple steps.

--SNIPPET: conversableagentchat.py

```python
# TEMPORARY, THIS WILL BE REPLACED BY ABOVE SNIPPET

# 1. Import our agent class
from autogen import ConversableAgent

# 2. Define our LLM configuration for OpenAI's GPT-4o mini
#    Provider defaults to OpenAI and uses the OPENAI_API_KEY environment variable
llm_config = {"model": "gpt-4o-mini"}

# 3. Create our agent
my_agent = ConversableAgent(
    name="helpful_agent",
    llm_config=llm_config,
    system_message="You are a poetic AI assistant",
)

# 4. Chat directly with our agent
my_agent.run("In one sentence, what's the big deal about AI?")
```

Let's break it down:

1. Import `ConversableAgent`, you'll find the most popular classes available directly from `autogen`.

2. Create our LLM configuration to define the LLM that our agent will use.

3. Create our ConversableAgent give them a unique name, and use `system_message` to define their purpose.

4. Chat with the agent using their `run` method, passing in our starting message.

```console
human (to helpful_agent):

In one sentence, what's the big deal about AI?

--------------------------------------------------------------------------------

>>>>>>>> USING AUTO REPLY...
helpful_agent (to human):

AI’s a marvel that transforms the mundane,
Empowering minds, making tasks less a strain.

--------------------------------------------------------------------------------
```

# Human in the loop

If you run the previous example you'll be able to chat with the agent and this is because another agent was automatically created to represent you, the human in the loop, when using an agent's `run` method.

As you build your own workflows, you'll want to create your own *human in the loop* agents and decide if and how to use them. To do so, simply use the ConversableAgent and set the `human_input_mode` to `ALWAYS`.

Let's start to build a more useful scenario, a classroom lesson planner, and create our human agent.

--SNIPPET: humanintheloop.py

```python
# TEMPORARY, THIS WILL BE REPLACED BY ABOVE SNIPPET

from autogen import ConversableAgent
llm_config = {"model": "gpt-4o-mini"}

planner_system_message = """You are a classroom lesson agent.
Given a topic, write a lesson plan for a fourth grade class.
Use the following format:
<title>Lesson plan title</title>
<learning_objectives>Key learning objectives</learning_objectives>
<script>How to introduce the topic to the kids</script>
"""

lesson_planner = ConversableAgent(
    name="lesson_agent",
    llm_config=llm_config,
    system_message=planner_system_message,
)

# 1. Create our human input agent
the_human = ConversableAgent(
    name="human",
    human_input_mode="ALWAYS",
)

# 2. Initiate our chat between the agents
the_human.initiate_chat(recipient=lesson_planner, message="Today, let's introduce our kids to the solar system.")
```

1. Create a second agent and set its `human_input_mode` with no `llm_config` required.

2. Our `the_human` agent starts a conversation by sending a message to `lesson_planner`. An agent's `initiate_chat` method is used to start a conversation between two agents.

# Many agents

Many hands make for light work, so it's time to move on from our simple two-agent conversations and think about orchestrating workflows containing many agents, a strength of the AG2 framework.

There are two mechanisms for building multi-agent workflows, GroupChat and Swarm.

GroupChat contains a number of built-in conversation patterns to determine the next agent. You can also define your own.

Swarm is a conversation pattern based on agents with handoffs. There's a shared context and each agent has tools and the ability to transfer control to other agents. The [original swarm concept](https://github.com/openai/swarm) was created by OpenAI.

:::note
We'll refer to *conversation patterns* throughout the documentation - they are simply a structured way of organizing the flow between agents.
:::

## GroupChat

`GroupChat` has four built-in conversation patterns:

| Method | Agent selection|
| --- | --- |
| `auto` (default) | Automatic, chosen by the `GroupChatManager` using an LLM |
| `round_robin` | Sequentially in their added order |
| `random` | Randomly |
| `manual` | Selected by you at each turn |
| *Callable* | Create your own flow |

Coordinating the `GroupChat` is the `GroupChatManager`, an agent that provides a way to start and resume multi-agent chats.

Let's enhance our lesson planner example to include a lesson reviewer and a teacher agent.

:::tip
You can start any multi-agent chats using the `initiate_chat` method
:::

--SNIPPET: groupchat.py

```python
# TEMPORARY, THIS WILL BE REPLACED BY ABOVE SNIPPET

from autogen import ConversableAgent, GroupChat, GroupChatManager
llm_config = {"model": "gpt-4o-mini"}

planner_message = """You are a classroom lesson agent.
Given a topic, write a lesson plan for a fourth grade class.
Use the following format:
<title>Lesson plan title</title>
<learning_objectives>Key learning objectives</learning_objectives>
<script>How to introduce the topic to the kids</script>
"""

# 1. Add a 'description' for our planner and reviewer agents
planner_description = "Creates or revises lesson plans."

lesson_planner = ConversableAgent(
    name="planner_agent",
    llm_config=llm_config,
    system_message=planner_message,
    description=planner_description,
)

reviewer_message = """You are a classroom lesson reviewer.
You compare the lesson plan to the fourth grade curriculum and provide a maximum of 3 recommended changes.
Provide only one round of reviews to a lesson plan.
"""

reviewer_description = """Provides one round of reviews to a lesson plan
for the lesson_planner to revise."""

lesson_reviewer = ConversableAgent(
    name="reviewer_agent",
    llm_config=llm_config,
    system_message=reviewer_message,
    description=reviewer_description,
)

# 2. The teacher's system message can also be used for the description, so we don't define it
teacher_message = """You are a classroom teacher.
You decide topics for lessons and work with a lesson planner.
and reviewer to create and finalise lesson plans.
When you are happy with a lesson plan, output "DONE!".
"""

teacher = ConversableAgent(
    name="teacher_agent",
    llm_config=llm_config,
    system_message=teacher_message,
    # 3. Our teacher can end the conversation by saying DONE!
    is_termination_msg=lambda x: "DONE!" in (x.get("content", "") or "").upper(),
)

# 4. Create the GroupChat with agents and selection method
groupchat = GroupChat(
    agents=[teacher, lesson_planner, lesson_reviewer],
    speaker_selection_method="auto",
    messages=[],
)

# 5. Our GroupChatManager will manage the conversation and uses an LLM to select the next agent
manager = GroupChatManager(
    name="group_manager",
    groupchat=groupchat,
    llm_config=llm_config,
)

# 6. Starting a chat with the GroupChatManager as the recipient kicks off the group chat
teacher.initiate_chat(recipient=manager, message="Today, let's introduce our kids to the solar system.")
```
1. Separate to `system_message`, we add a `description` for our planner and reviewer agents and this is used exclusively for the purposes of determining the next agent by the `GroupChatManager` when using automatic speaker selection.

2. The teacher's `system_message` is suitable as a description so, by not setting it, the `GroupChatManager` will use the `system_message` for the teacher when determining the next agent.

3. The workflow is ended when the teacher's message contains the phrase "DONE!".

4. Construct the `GroupChat` with our agents and selection method as automatic (which is the default).

5. `GroupChat` requires a `GroupChatManager` to manage the chat and an LLM configuration is needed because they'll use an LLM to decide the next agent.

6. Starting a chat with the `GroupChatManager` as the `recipient` kicks off the group chat.

```console
teacher_agent (to group_manager):

Today, let's introduce our kids to the solar system.

--------------------------------------------------------------------------------

Next speaker: planner_agent


>>>>>>>> USING AUTO REPLY...
planner_agent (to group_manager):

<title>Exploring the Solar System</title>
<learning_objectives>
1. Identify and name the planets in the solar system.
2. Describe key characteristics of each planet.
3. Understand the concept of orbit and how planets revolve around the sun.
4. Develop an appreciation for the scale and structure of our solar system.
</learning_objectives>
<script>
"Good morning, class! Today, we are going to embark on an exciting journey through our solar system. Have any of you ever looked up at the night sky and wondered what those bright dots are? Well, those dots are often stars, but some of them are planets in our own solar system!

To start our adventure, I want you to close your eyes and imagine standing on a giant spaceship, ready to zoom past the sun. Does anyone know what the sun is? (Pause for responses.) Right! The sun is a star at the center of our solar system.

Today, we are going to learn about the planets that travel around the sun - but not just their names, we're going to explore what makes each of them special! We will create a model of the solar system together, and by the end of the lesson, you will be able to name all the planets and tell me something interesting about each one.

So, are you ready to blast off and discover the wonders of space? Let's begin!"
</script>

--------------------------------------------------------------------------------

Next speaker: reviewer_agent


>>>>>>>> USING AUTO REPLY...
reviewer_agent (to group_manager):

**Review of the Lesson Plan: Exploring the Solar System**

1. **Alignment with Curriculum Standards**: Ensure that the lesson includes specific references to the fourth grade science standards for the solar system. This could include discussing gravity, the differences between inner and outer planets, and the role of the sun as a stable center of our solar system. Adding this information will support a deeper understanding of the topic and ensure compliance with state educational standards.

2. **Interactive Activities**: While creating a model of the solar system is a great hands-on activity, consider including additional interactive elements such as a group discussion or a game that reinforces the learning objectives. For instance, incorporating a "planet facts" game where students can share interesting facts about each planet would further engage the students and foster collaborative learning.

3. **Assessment of Learning**: It would be beneficial to include a formative assessment to gauge students' understanding at the end of the lesson. This could be a quick quiz, a group presentation about one planet, or a drawing activity where students depict their favorite planet and share one fact about it. This will help reinforce the learning objectives and provide students with an opportunity to demonstrate their knowledge.

Making these adjustments will enhance the educational experience and align it more closely with fourth-grade learning goals.

--------------------------------------------------------------------------------

Next speaker: planner_agent


>>>>>>>> USING AUTO REPLY...
planner_agent (to group_manager):

**Revised Lesson Plan: Exploring the Solar System**

<title>Exploring the Solar System</title>
<learning_objectives>
1. Identify and name the planets in the solar system according to grade-level science standards.
2. Describe key characteristics of each planet, including differences between inner and outer planets.
3. Understand the concept of orbit and how gravity keeps planets revolving around the sun.
4. Develop an appreciation for the scale and structure of our solar system and the sun's role as the center.
</learning_objectives>
<script>
"Good morning, class! Today, we are going to embark on an exciting journey through our solar system. Have any of you ever looked up at the night sky and wondered what those bright dots are? Well, those dots are often stars, but some of them are planets in our own solar system!

To start our adventure, I want you to close your eyes and imagine standing on a giant spaceship, ready to zoom past the sun. Does anyone know what the sun is? (Pause for responses.) That's right! The sun is a star at the center of our solar system.

Now, today's goal is not only to learn the names of the planets but also to explore what makes each of them unique. We'll create a model of the solar system together, and through this process, we will also talk about the differences between the inner and outer planets.

As part of our exploration, we'll play a fun "planet facts" game. After learning about the planets, I will divide you into small groups, and each group will get a planet to research. You’ll find interesting facts about the planet, and we will come together to share what you discovered!

At the end of our lesson, I'll give you a quick quiz to see how much you've learned about the planets, or you can draw your favorite planet and share one cool fact you found with the class.

So, are you ready to blast off and discover the wonders of space? Let's begin!"
</script>

**Interactive Activities**:
- **Planet Facts Game**: After discussing each planet, students will work in groups to find and share a unique fact about their assigned planet.

**Assessment of Learning**:
- **Individual Reflection Drawing**: Students draw their favorite planet and write one fact about it.
- **Quick Quiz**: A short quiz at the end to assess understanding of the planets and their characteristics.

This revised plan incorporates additional interactive elements and assessments that align with educational standards and enhance the overall learning experience.

--------------------------------------------------------------------------------

Next speaker: teacher_agent


>>>>>>>> USING AUTO REPLY...
teacher_agent (to group_manager):

DONE!

--------------------------------------------------------------------------------
```

## Swarm

Swarms provide controllable flows between agents that are determined at the agent-level. You define hand-off, post-tool, and post-work transitions from an agent to another agent (or to end the swarm).

When designing your swarm, think about your agents in a diagram with the lines between agents being your hand-offs. Each line will have a condition statement which an LLM will evaluate. Control stays with an agent while they execute their tools and once they've finished with their tools the conditions to transition will be evaluated.

One of the unique aspects of a swarm is a shared context. ConversableAgents have a context dictionary but in a swarm that context is made common across all agents, allowing a state of the workflow to be maintained and viewed by all agents. This context can also be used within the hand off condition statements, providing more control of transitions.

AG2's swarm has a number of unique capabilities, find out more in our [Swarm documentation](https://docs.ag2.ai/docs/topics/swarm).

Here's our lesson planner workflow using AG2's Swarm.

--SNIPPET: swarm.py

```python
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

# 3. Our agents now have tools to use (functions above)
planner_message = """You are a classroom lesson planner.
Given a topic, write a lesson plan for a fourth grade class.
If you are given revision feedback, update your lesson plan and record it.
Use the following format:
<title>Lesson plan title</title>
<learning_objectives>Key learning objectives</learning_objectives>
<script>How to introduce the topic to the kids</script>
"""

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
# allowing reviews, otherwise transition to the teacher
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

# Lesson reviewer will review the plan and return control to the planner if there's
# no plan to review, otherwise it will provide a review and
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

# Tools

Agents gain significant utility through tools because they provide access to external data, APIs, and functionality.

In AG2, tool use is managed using two agents, one decides which tools to use (via their LLM) and another executes the tool.

Adding a tool to an agent is as simple as registering it with the agent.

...

# Other topics TBD

# Ending a chat

# Structured outputs

# Code execution

# Advanced Agents

- CaptainAgent
- ReasoningAgent
- DocumentAgent
- WebSurferAgent
- DiscordAgent

# Agent Capabilities

# How do I ...
