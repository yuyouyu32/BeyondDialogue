
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from openai import AsyncOpenAI, OpenAI

from .cost import Cost
from .llm_client import LLMClient
from .utils import *


class BaseOpenAIClient(LLMClient):
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, client_type: str = 'openAI') -> None:
        self._client_types = {'openAI', 'deepseek', '01-AI', 'baichuan'} 
        dir_path = os.path.dirname(os.path.abspath(__file__))
        models_path = os.path.join(dir_path, 'models.json')
        with open(models_path) as f:
            self._models: dict = json.load(f)
        if base_url and api_key:
            self.base_url = base_url
            self.api_key = api_key
        else:
            if client_type not in self._client_types:
                raise Exception(f'Invalid client type: {client_type}, please choose from {self._client_types}')
            if client_type == 'openAI':
                self.base_url = os.environ.get('OPENAI_BASE_URL', 'http://api-xxxxx')
                self.api_key = os.environ.get('OPENAI_API_KEY', 'sk-xxxx')
            elif client_type == 'deepseek':
                self.base_url = 'https://api.deepseek.com'
                self.api_key = os.environ.get('DEEPSEEK_API_KEY', 'sk-xxxx')
            elif client_type == '01-AI':
                self.base_url = "https://api.lingyiwanwu.com/v1"
                self.api_key = os.environ.get('01AI_API_KEY', 'sk-xxxx')
            elif client_type == 'baichuan':
                self.base_url = "https://api.baichuan-ai.com/v1/"
                self.api_key = os.environ.get('BAICHUAN_API_KEY', 'sk-xxxx')
        self.client_type = client_type
        
    def get_client_type(self) -> Tuple[str]:
        '''
        Get the valid client type.
        
        Returns:
            client_types: Valid client type.
        '''

        return self._client_types
    
    
    def calculate_cost(self, prompt_tokens : int, completion_tokens: int, model: str = 'gpt-3.5-turbo'):
        '''
        Calculate the cost for a given number of tokens and model.
        
        Parameters:
            prompt_tokens: Number of tokens in the prompt.
            completion_tokens: Number of tokens in the completion.
            model: Model to be used, model can be gpt-3.5-turbo (default), gpt-4, gpt-4-32k, gpt-4-turbo
        Returns:
            Cost in $.
        '''
        if model not in self._models.keys():
            print(f'Model {model} is not supported.')
            return 0, 'RMB'
        else:
            if 'price' not in self._models[model]:
                return 0, 'RMB'
            else:
                price = self._models[model]['price']
                return (prompt_tokens / 1000) * price['prompt'] + (completion_tokens / 1000) * price['complete'], price['currency']
                
        

class OpenAIClient(BaseOpenAIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        
    @retry_on_failure(max_retries= MaxRetries, delay=Delay)
    def call(self, messages: List[Dict[str, str]], model: str = 'gpt-3.5-turbo', n: int=5, temperature: Optional[float] = None) -> List[str]:
        '''
        Synchronous call to OpenAI API.
        
        Parameters:
            messages: List of messages to be sent to OpenAI API.
            model: Model to be used, model can be gpt-3.5-turbo (default), gpt-4, gpt-4-32k, chat-bison-001 (Google Bard), gpt-4-turbo ...
            n: Number of responses to be generated.
            temperature: Temperature for sampling.
        
        Returns:
            response: Response from OpenAI API.
            cost: Cost in $ or ¥.
        '''
        if model == 'ERNIE-Bot' and n > 1:
            raise Exception('ERNIE-Bot only supports n=1')
        if model in {"claude-3-opus"}:
            if messages[0]['role'] == 'system':
                system_message = messages.pop(0)
                usr_message = messages[0]['content']
                messages[0]['content'] = system_message['content'] + '\n' + usr_message
        call_params = {
            "messages": messages,
            "model": model,
            "n": n
        }

        if temperature:
            call_params["temperature"] = temperature
        chat_completion = self.client.chat.completions.create(**call_params)

        if model == 'ERNIE-Bot':
            rsps = [chat_completion.result]
        else:
            if chat_completion.choices is None:
                error = chat_completion.error
                if model == 'moonshot-v1-128k' and 'rejected' in error['message']:
                    return ['##High Risk##'] * n, 0
                else:
                    raise Exception(f'{str(error)}')
            
            rsps = [chat_completion.choices[i].message.content for i in range(n)]

        money, currency = self.calculate_cost(chat_completion.usage.prompt_tokens, chat_completion.usage.completion_tokens, model)
        input_tokens = chat_completion.usage.prompt_tokens
        output_tokens = chat_completion.usage.completion_tokens
        cost = Cost(input_tokens_k=input_tokens/1000, output_tokens_k=output_tokens/1000, money=money, currency=currency)
        return rsps, cost
    
class AsyncOpenAIClient(BaseOpenAIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)

    async def call(self, messages: List[Dict[str, str]], model: str = 'gpt-3.5-turbo', n=5) -> str:
        '''
        Asynchronous call to OpenAI API.
        
        Parameters:
            messages: List of messages to be sent to OpenAI API.
            model: Model to be used, model can be gpt-3.5-turbo (default), gpt-4, gpt-4-32k, chat-bison-001 (Google Bard), gpt-4-turbo ...
        
        Returns:
            response: Response from OpenAI API.
            cost: Cost in $.
        '''
        async def request():
            chat_completion = await self.client.chat.completions.create(messages=messages, model=model)
            cost = self.calculate_cost(chat_completion.usage.prompt_tokens, chat_completion.usage.completion_tokens, model, n=n)
            return chat_completion.choices[0].message.content, cost

        resposne, cost = await request()
        return resposne, cost
    

def unit_test() -> None:
    client = OpenAIClient(client_type = 'openAI')
    messages = [
        {
            "role": "user",
            "content": "你是谁啊?"
        }
    ]
    model = 'moonshot-v1-128k'
    response, cost = client.call(messages=messages, model=model, n=1)
    print(response, cost)

if __name__ == '__main__':
    unit_test()