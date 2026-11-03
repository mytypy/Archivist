import asyncio

import httpx
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from constants.prompts import VALIDATOR
from schemas.model.model import SafetyOutput


class Agent:
    
    def __init__(self, model_name: str, system_prompt: str, pydantic_object, url: str,  **arguments):
        self.model = model_name
        self.system_prompt = system_prompt
        
        self.llm = ChatOpenAI(model=model_name,
                              api_key='qwdqwd',
                              base_url=url,
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

PROMPT = 'Что задали на завтра?'


agent = Agent('qwen2.5:7b-instruct-q4_K_M', system_prompt=VALIDATOR, pydantic_object=SafetyOutput, url='http://localhost:11434/v1')


async def main():
    data = {'input_data': PROMPT}
    
    response = await agent.invoke(data)
    
    print(response)
    

if __name__ == '__main__':
    asyncio.run(main())