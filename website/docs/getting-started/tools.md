# Tools

Agents gain significant utility through tools as they provide access to external data, APIs, and functionality.

In AG2, using tools is done in two parts, an agent *suggests* which tools to use (via their LLM) and another *executes* the tool.

::note
In a conversation the executor agent must follow the agent that suggests a tool.
::

In the swarm example above, we attached tools to our agents and, as part of the swarm, AG2 created a tool executor agent to run recommended tools. Typically, you'll create two agents, one to decide which tool to use and another to execute it.

--SNIPPET: toolregister.py

```python
# TEMPORARY, THIS WILL BE REPLACED BY ABOVE SNIPPET

from autogen import ConversableAgent, register_function
from typing import Annotated
from datetime import datetime
llm_config = {"model": "gpt-4o-mini"}

# 1. Our tool, returns the day of the week for a given date
def get_weekday(date_string: Annotated[str, "Format: YYYY-MM-DD"]) -> str:
    date = datetime.strptime(date_string, '%Y-%m-%d')
    return date.strftime('%A')

# 2. Agent for determining whether to run the tool
date_agent = ConversableAgent(
    name="date_agent",
    system_message="You get the day of the week for a given date.",
    llm_config=llm_config,
)

# 3. And an agent for executing the tool
executor_agent = ConversableAgent(
    name="executor_agent",
    human_input_mode="NEVER",
)

# 4. Registers the tool with the agents, the description will be used by the LLM
register_function(
    get_weekday,
    caller=date_agent,
    executor=executor_agent,
    description="Get the day of the week for a given date",
)

# 5. Two-way chat ensures the executor agent follows the suggesting agent
chat_result = executor_agent.initiate_chat(
    recipient=date_agent,
    message="I was born on the 25th of March 1995, what day was it?",
    max_turns=2,
)

print(chat_result.chat_history[-1]["content"])
```
1. Here's the tool, a function, that we'll attach to our agents, the `Annotated` parameter will be  included in the call to the LLM so it understands what the `date_string` needs.

2. The date_agent will determine whether to use the tool, using its LLM.

3. The executor_agent will run the tool and return the output as its reply.

4. Registering the tool with the agents and giving it a description to help the LLM determine.

5. We have a two-way chat, so after the date_agent the executor_agent will run and, if it sees that the date_agent suggested the use of the tool, it will execute it.

```console
executor_agent (to date_agent):

I was born on the 25th of March 1995, what day was it?

--------------------------------------------------------------------------------

>>>>>>>> USING AUTO REPLY...
date_agent (to executor_agent):

***** Suggested tool call (call_iOOZMTCoIVVwMkkSVu04Krj8): get_weekday *****
Arguments:
{"date_string":"1995-03-25"}
****************************************************************************

--------------------------------------------------------------------------------

>>>>>>>> EXECUTING FUNCTION get_weekday...
Call ID: call_iOOZMTCoIVVwMkkSVu04Krj8
Input arguments: {'date_string': '1995-03-25'}
executor_agent (to date_agent):

***** Response from calling tool (call_iOOZMTCoIVVwMkkSVu04Krj8) *****
Saturday
**********************************************************************

--------------------------------------------------------------------------------

>>>>>>>> USING AUTO REPLY...
date_agent (to executor_agent):

It was a Saturday.

--------------------------------------------------------------------------------
```

Alternatively, you can use decorators to register a tool. So, instead of using `register_function`, you can register them with the function definition.
```python
@date_agent.register_for_llm(description="Get the day of the week for a given date")
@executor_agent.register_for_execution()
def get_weekday(date_string: Annotated[str, "Format: YYYY-MM-DD"]) -> str:
    date = datetime.strptime(date_string, '%Y-%m-%d')
    return date.strftime('%A')
```

Next > structured-outputs.md
