language = "cn"
model_config = {
    'glm-4-9b-chat': {"ip": '127.0.0.1', "port": 8000},
    'Index-1.9B-Character':  {"ip": '127.0.0.1', "port": 8001},
    'Qwen2-7B-Instruct':  {"ip": '127.0.0.1', "port": 8002},
    'Yi-1.5-9B-Chat':  {"ip": '127.0.0.1', "port": 8003},
    "glm-4-9b-RP" : {"ip": '127.0.0.1', "port": 8004},
    "Qwen2-7B-RP": {"ip": '127.0.0.1', "port": 8005},
    "Yi-1.5-9B-RP": {"ip": '127.0.0.1', "port": 8006},
    "Qwen2-7B-RP-CC": {"ip": '127.0.0.1', "port": 8026},
    "Qwen2-7B-RP-CC-CSREP": {"ip": '127.0.0.1', "port": 8018},
    "Qwen2-7B-RPA-CC-CESRP": {"ip": '127.0.0.1', "port": 8027},
    "CharacterGLM": {"ip": '127.0.0.1', "port": 8009},
    "Qwen2-7B-RPA-CC": {"ip": '127.0.0.1', "port": 8028},
    "Qwen2-7B-RPA-CC-wo-S": {"ip": '127.0.0.1', "port": 8029},
    "Qwen2-7B-RPA-CC-wo-R": {"ip": '127.0.0.1', "port": 8030},
    "Qwen2-7B-RPA-CC-wo-P": {"ip": '127.0.0.1', "port": 8031},
    "Qwen2-7B-RPA-CC-wo-E": {"ip": '127.0.0.1', "port": 8032},
    "Qwen2-7B-RPA-CC-wo-C": {"ip": '127.0.0.1', "port": 8033},
    "Mistral-Nemo-Instruct-2407":  {"ip": '127.0.0.1', "port": 8034},
    "Mistral-Nemo-12B-RP-CC":  {"ip": '127.0.0.1', "port": 8035},
    "Mistral-Nemo-12B-RPA-CC":  {"ip": '127.0.0.1', "port": 8036},
    "Mistral-Nemo-RPA-CC-CESRP":  {"ip": '127.0.0.1', "port": 8037},
}

MaxGenRoleNum = 10
DialogueModels = []
# ["gpt-4o", "claude-3-opus", "gpt-3.5-turbo", "moonshot-v1-8k", "yi-large-turbo", "deepseek-chat", "Baichuan4", "hunyuan", "Index-1.9B-Character", "Baichuan-NPC-Turbo", "Qwen2-7B-Instruct", "glm-4-9b-chat", "Yi-1.5-9B-Chat", "Qwen2-7B-RP-CC","Qwen2-7B-RPA-CC-CESRP"] 
# ["Qwen2-7B-RPA-CC-wo-C", "Qwen2-7B-RPA-CC-wo-E", "Qwen2-7B-RPA-CC-wo-S", "Qwen2-7B-RPA-CC-wo-R", "Qwen2-7B-RPA-CC-wo-P"]
TestModels = [] # "Mistral-Nemo-Instruct-2407", "Mistral-Nemo-12B-RP-CC", "Mistral-Nemo-12B-RPA-CC",  "Mistral-Nemo-RPA-CC-CESRP"
# ["gpt-4o", "claude-3-opus", "gpt-3.5-turbo", "moonshot-v1-8k", "yi-large-turbo", "deepseek-chat", "Baichuan4", "hunyuan", "Index-1.9B-Character", "CharacterGLM", "Baichuan-NPC-Turbo",  "Qwen2-7B-Instruct", "Qwen2-7B-RP-CC", "Qwen2-7B-RPA-CC", "Qwen2-7B-RPA-CC-CESRP"]
# ["Qwen2-7B-RPA-CC-wo-C", "Qwen2-7B-RPA-CC-wo-E", "Qwen2-7B-RPA-CC-wo-S", "Qwen2-7B-RPA-CC-wo-R", "Qwen2-7B-RPA-CC-wo-P", "Qwen2-7B-RPA-CC-CESRP"]
# t_TestModel = {"Qwen2-7B-Instruct", "Qwen2-7B-RPA-CC-CESRP"}
t_TestModel = {"Mistral-Nemo-Instruct-2407", "Mistral-Nemo-RPA-CC-CESRP"}
MetricModels = ["gpt-4o", "claude-3-opus", "gpt-3.5-turbo", "moonshot-v1-8k", "yi-large-turbo", "deepseek-chat", "Baichuan4", "hunyuan", "glm-4-9b-chat", "Yi-1.5-9B-Chat", "Index-1.9B-Character", "CharacterGLM", "Baichuan-NPC-Turbo",  "Qwen2-7B-Instruct", "Qwen2-7B-RP-CC", "Qwen2-7B-RPA-CC", "Qwen2-7B-RPA-CC-CESRP", "Mistral-Nemo-Instruct-2407", "Mistral-Nemo-12B-RP-CC", "Mistral-Nemo-12B-RPA-CC", "Mistral-Nemo-RPA-CC-CESRP"]