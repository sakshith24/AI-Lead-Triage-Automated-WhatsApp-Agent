import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()

app = FastAPI(title="AI Lead Triage Microservice", version="1.0")

# Define the structured output model using Pydantic
class LeadAnalysis(BaseModel):
    lead_score: int = Field(description="Numerical lead score from 1 to 100 based on budget, urgency, and company size.")
    category: Literal["Hot", "Warm", "Cold"] = Field(description="Categorization of the lead.")
    inferred_intent: str = Field(description="Brief summary of what the lead is looking to achieve or solve.")
    personalized_whatsapp_message: str = Field(description="A professional, engaging, industry-tailored follow-up message ready to send via WhatsApp.")

# Request schema for incoming webhook payload from n8n
class LeadPayload(BaseModel):
    name: str
    email: str
    company: str
    industry: str
    message: str
    budget: str = "Not specified"

@app.post("/triage-lead", response_model=LeadAnalysis)
async def triage_lead(lead: LeadPayload):
    try:
        # Initialize LLM
        llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        
        # Set up Pydantic parser
        parser = PydanticOutputParser(pydantic_object=LeadAnalysis)
        
        # Prompt Engineering with formatting instructions
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an expert AI Sales Development Representative (SDR) and lead qualification specialist. "
             "Analyze the incoming lead data, evaluate their potential, score them, determine their category (Hot/Warm/Cold), "
             "and draft a high-converting, personalized WhatsApp follow-up message tailored to their specific industry.\n\n"
             "{format_instructions}"),
            ("user", 
             "Lead Details:\n"
             "- Name: {name}\n"
             "- Email: {email}\n"
             "- Company: {company}\n"
             "- Industry: {industry}\n"
             "- Message: {message}\n"
             "- Budget: {budget}")
        ])
        
        # Format prompt with parser instructions
        formatted_prompt = prompt.partial(format_instructions=parser.get_format_instructions())
        
        chain = formatted_prompt | llm | parser
        
        # Invoke AI
        result = chain.invoke({
            "name": lead.name,
            "email": lead.email,
            "company": lead.company,
            "industry": lead.industry,
            "message": lead.message,
            "budget": lead.budget
        })
        
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)