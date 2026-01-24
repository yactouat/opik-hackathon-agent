import os
from typing import Optional, TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from opik import configure

from constants import BASE_MODEL
from models.InteractionWithAPersonCard import InteractionWithAPersonCard

configure()


class GraphState(TypedDict):
    input: Optional[str] = None
    interaction_card: Optional[InteractionWithAPersonCard] = None
    error: Optional[str] = None


def extract_interaction_node(state):
    """
    Uses Google Gemini to extract structured interaction data from input text.
    """
    input = state.get("input", "").strip()
    
    if not input:
        return {"error": "No input text provided"}
    
    llm = ChatGoogleGenerativeAI(
        model=BASE_MODEL,
        google_api_key=os.environ.get("GOOGLE_API_KEY"),
    )
    
    structured_llm = llm.with_structured_output(InteractionWithAPersonCard)
    
    prompt = f"""Extract information about an interaction with a person from the following text, following the 5 Whys framework (Who, Where, When, Why, How).

Text:
{input}
"""
    
    try:
        result = structured_llm.invoke(prompt)
        return {"interaction_card": result}
    except Exception as e:
        return {"error": str(e)}


workflow = StateGraph(GraphState)
workflow.add_node("extract_interaction", extract_interaction_node)

workflow.set_entry_point("extract_interaction")
workflow.add_edge("extract_interaction", END)

extract_interaction_with_a_person_card_graph = workflow.compile()

if __name__ == "__main__":
    from opik.integrations.langchain import OpikTracer
    from dotenv import load_dotenv
    load_dotenv()

    tracer = OpikTracer(graph=extract_interaction_with_a_person_card_graph.get_graph(xray=True))
    inputs = {"input": "I met John at the coffee shop yesterday. We talked about AI and machine learning for hours. It was a really stimulating conversation!"}
    result = extract_interaction_with_a_person_card_graph.invoke(
        inputs,
        config={
            "callbacks": [tracer],
        },
    )
    print(result)
