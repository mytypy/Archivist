import httpx
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from core.config import AppSettings


class Agent:
    """Класс для взаимодейтсвия с моделью"""
    
    def __init__(self, model_name: str, system_prompt: str, pydantic_object, **arguments):
        self.model = model_name
        self.system_prompt = system_prompt
        settings = AppSettings()
        
        self.llm = ChatOpenAI(model=model_name,
                              api_key='qwdqwd',
                              base_url=settings.MODEL_URL,
                              model_kwargs={"response_format": {"type": "json_object"}},
                              timeout=httpx.Timeout(300.0, read=300.0, connect=60.0),
                              **arguments)
        
        structured_llm = self.llm.with_structured_output(pydantic_object)
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input_data}")
        ])

        self.chain = prompt | structured_llm 

    async def invoke(self, query: dict):
        return await self.chain.ainvoke(query)
        
    def __str__(self):
        return f'<Model {self.model}>'
    
    def __repr__(self):
        return f'<Model {self.model}>'