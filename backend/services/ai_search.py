from pydantic import BaseModel, Field
from typing import Optional, Literal
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", response_mime_type="application/json", temperature = 0)


class AISearch(BaseModel):
    domain: Optional[str] = Field(description="Enter the domain of the book.")
    max_price: Optional[int] = Field(description="Enter your budget.")
    sort_by: Optional[Literal["id", "title", "price", "created_at"]] = Field(
        description="Sort books by id, title, price, or created_at")
    order: Optional[Literal["asc", "desc"]] = Field(description="Sorting order: ascending or descending")


parser = PydanticOutputParser(pydantic_object = AISearch)

template = PromptTemplate(
    template = """
You are an assistant that extracts structured filters from a user's natural language query
for a book inventory and order system.

User query:
"{query}"

Your task:
- Extract relevant filters from the query.
- If a field is not mentioned, return null.
- Do NOT invent values.
- Return ONLY valid JSON.
- The JSON must strictly follow the schema below.

{format_instructions}

""",
    input_variables=['query'],
    partial_variables = {'format_instructions':parser.get_format_instructions()}
)


chain = template | model | parser






