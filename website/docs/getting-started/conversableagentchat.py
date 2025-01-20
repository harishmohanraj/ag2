# 1. Import our agent class
from autogen import ConversableAgent

# 2. Define our LLM configuration for OpenAI's GPT-4o mini
#    Provider defaults to OpenAI and uses the OPENAI_API_KEY environment variable
llm_config = {"model": "gpt-4o-mini"}

# 3. Create our agent
my_agent = ConversableAgent(
    name="helpful_agent",
    llm_config=llm_config,
)

# 4. Chat directly with our agent
my_agent.run("In one sentence, what's the big deal about AI?")
