from langchain_community.chat_models.openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Optional
import json

from app.vector_store import VectorStore
from app.config import settings

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            max_tokens=500,
            api_key=settings.openai_api_key
        )
        self.vector_store = VectorStore()
    
    def create_system_prompt(self, client_data: Dict, relevant_knowledge: List[Dict]) -> str:
        knowledge_context = "\n".join([doc['content'] for doc in relevant_knowledge])
        
        business_hours_str = ""
        if client_data.get('business_hours'):
            business_hours_str = json.dumps(client_data['business_hours'], indent=2)
        
        return f"""You are an AI assistant representing {client_data['business_name']}.
        
Business Information:
- Business Name: {client_data['business_name']}
- Industry: {client_data.get('industry', 'N/A')}
- Services: {client_data.get('services', 'N/A')}
- Business Hours: {business_hours_str}
- Phone: {client_data['phone_number']}

Relevant Knowledge Base:
{knowledge_context}

FAQs:
{client_data.get('faqs', 'No FAQs available')}

Instructions:
1. You are a professional, friendly receptionist for this business
2. Answer questions using the knowledge base and business information provided
3. If someone wants to book an appointment, collect: name, phone, preferred date/time, service type
4. Always stay in character as a representative of this business
5. Be helpful, professional, and concise
6. If you don't know something, say you'll have someone get back to them
7. For appointment booking, confirm details before proceeding

When booking appointments, respond with: "BOOK_APPOINTMENT: {{appointment_details_json}}"
"""
    
    def generate_response(self, client_data: Dict, user_message: str, conversation_history: List[Dict]) -> str:
        # Search for relevant knowledge
        relevant_knowledge = self.vector_store.search_knowledge(
            client_data['client_id'], 
            user_message, 
            k=3
        )
        
        # Create system prompt
        system_prompt = self.create_system_prompt(client_data, relevant_knowledge)
        
        # Build conversation history
        messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                messages.append(AIMessage(content=msg['content']))
        
        # Add current message
        messages.append(HumanMessage(content=user_message))
        
        # Generate response
        response = self.llm.invoke(messages)
        return response.content