### GitHub Codespaces

Before we jump into some code, each code block will have a button that allows you to open it in GitHub Codespaces and start playing with AG2 yourself, inside a fully configured environment.

Add an OPENAI_API_KEY secret to your GitHub Codespaces so your agents can use an LLM. See the [instructions here](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces).

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

Next > human-in-the-loop.md
