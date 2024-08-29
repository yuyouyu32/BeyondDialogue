# LLMClient子模块仓库

本仓库被设计为作为其他仓库的LLMs调用子模块使用。它包含调用各种支持`OpenAI`接口LLMs功能，可以被其他项目引用，以便重用代码而不必复制代码到每一个项目中。
## 如何调用

```python
from LLMClients import OpenAIClient

client = OpenAIClient(client_type = 'openAI')
messages = [
    {
        "role": "user",
        "content": "你是谁啊?"
    }
]
model = 'gpt-3.5-turbo'
response, cost = client.call(messages=messages, model=model, n=1)
print(response, cost)
# response: ['你好！很高兴认识你。我是一个AI助手，我的目标是帮助用户解决问题和回答疑问。如果你有任何问题或需要帮助，请随时告诉我。']
# cost: Money: 0.00048 USD, Input Tokens: 0.024k, Output Tokens: 0.036k
```
