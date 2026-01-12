import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI

from langchain.messages import HumanMessage, AIMessage
from langchain.tools import tool
from tavily import TavilyClient

from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

print("Welcome to Personal Chef Agency!!!")


# model configuration
model = AzureChatOpenAI(
    api_key = os.getenv("AZURE_OPENAI_KEY"),
    api_version = os.getenv("AZURE_OPENAI_VERSION"),
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
)


# prompt
system_prompt = "You are an expert chef with years of experience, specializing in creating dishes from whatever ingredients are available. If ther are more that on dishes that can be made then give options to pick the one and then give the detailed recipe for that dish."


# tools
tavily_client = TavilyClient()

@tool
def web_search(query: str) -> str:
    """Return the relevent content for the user query from the internet"""
    return tavily_client.search(query)

# agent creation
agent = create_agent(
        model, 
        tools=[web_search], 
        system_prompt=system_prompt,
        checkpointer = InMemorySaver()    
    )


# config thread to keep track of the conversation
config = {"configurable":{"thread_id":1}}

print("What are you planning to make today..")
ingredients = input("You: ")

# res = agent.invoke(
#     {
#         "messages": [HumanMessage(content=f"What can I make from this ingredients: {ingredients}")]
#     },
#     config,
# )

print("AI: ",end="")
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": ingredients}]},
    stream_mode="messages", 
    config=config,
):
    print(chunk[0].content, end="")

# print("AI Personal Chef: ",res["messages"][-1].content)

while (True):
    # user input
    print(2*"\n")
    query2 = input("You: ")
    if query2.lower() in ['exit','quit','close','no']: 
        break
    
    
    print("AI: ",end="")
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": query2}]},
        stream_mode="messages",
        config=config,
    ):
        print(chunk[0].content, end="")

