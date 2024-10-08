RoleReference = """下面会有一些参考的角色：
{reference}
请设计与这些参考角色截然不同的全新角色。"""

RolePrompt = """你是一位经验丰富的创意写作导师，擅长构建创新的角色。
你需要设计一个全新角色的描述，该角色将与{role_name}对话，确保该角色与{role_name}的对话能够较好体现{role_name}角色的性格、人格和说话风格。
下面是{role_name}的一些基本信息：
性格：{character}
MBTI人格类型：{MBTI}
说话风格：{style}
所处世界：{world}

你需要根据{role_name}角色的特点，创造性地构建一个与其对话的全新角色设定，该角色不能出现在{role_name}相关的作品中。全新角色的描述应该包括角色的姓名和简单的人物描述，输出需要以json的形式输出，如
{{"chat_role": "角色名","role_des": "角色描述（不得超过100个字）"}}
{role_reference}
现在请你根据上述的信息创造一个独一无二的角色，注意输出的格式需要符合上述的要求。
"""

ScenePrompt = """你是一位经验丰富的编剧，擅长创作引人入胜的场景。
你需要创建一个场景描述，需要符合两个角色的设定，同时与角色所处的世界保持一致。
可供参考的例子：：
- {{"scene": "在爱情公寓内，胡一菲和陆展博讨论展博对宛瑜的好感。胡一菲鼓励展博勇敢追爱，并通过篮球赛的赌注来决定展博是否向宛瑜表白。"}}

下面是对话角色的一些基本信息：
角色A:
姓名：{role_name}
角色描述：{role_name}的性格是{character}，MBTI人格类型是{MBTI}，说话风格是{style}。
角色B:
姓名：{chat_role}
角色描述：{role_des}

角色所处世界：{world}

你需要根据角色AB的信息，构建一个引人入胜的场景，注意场景和人物的行为需要符合两个角色的设定，最好在50-100字，同时与角色所处的世界保持一致。输出需要以json的形式输出，如
{{"scene": "场景描述（50-100个字）"}}
现在请你根据上述的信息创造一个符合两位角色设定且引人入胜的场景，场景中不能直接出现人物的对话，注意输出的格式需要符合上述的要求。
"""

EmotionPrompt = """你是一位专业的心理学家，擅长分析人物情感和行为模式。
你需要根据对话角色的信息和对话发生的场景，赋予角色{role_name}在特定场景下的六种基本情绪：快乐、悲伤、厌恶、恐惧、惊讶和愤怒。
下面是一些对话角色和场景的相关信息：
角色A:
姓名：{role_name}
角色描述：{role_name}的性格是{character}，MBTI人格类型是{MBTI}，说话风格是{style}。
角色B:
姓名：{chat_role}
角色描述：{role_des}
场景：
{scene}

理解角色的描述和当前的场景，赋予角色{role_name}在该场景下说的话所体现的的六种基本情绪：快乐、悲伤、厌恶、恐惧、惊讶和愤怒。输出每一个基本情绪维度的分数到json格式中，0-10分，0分表示完全没有表现出该情绪，10分表示完全表现出该情绪。
请你用简短的几句话分析{role_name}在这个场景中应该体现的6种基本情绪的分数，避免一开始就简单陈述你的评估结果，以确保你的结论是正确的。最后用并且用json可解析的格式格式返回你的评估结果。具体格式如下：
{{"快乐": "快乐分数", "悲伤": "悲伤分数", "厌恶": "厌恶分数", "恐惧": "恐惧分数", "惊讶": "惊讶分数","愤怒": "愤怒分数"}}

现在，严格按照要求对场景和角色信息进行分析，并赋予{role_name}情绪分数，这个分数必须符合角色的设定和当前的场景，分析需要简短的几句话，不要太长，不要输出额外的内容，最后的情绪分数需要严格按照格式要求输出。
"""


RelationshipPrompt = """你是一位情感分析专家，精通心理学、人际关系评估，擅长通过角色性格和场景来初始化人物之间的关系亲密度。
你需要分析{role_name}角色和{chat_role}之间的关系亲密度，通过分析两个角色的信息和场景内容来初始化两个人物之间的亲密度。
下面是一些对话角色和场景的相关信息：
角色A:
姓名：{role_name}
角色描述：{role_name}的性格是{character}，MBTI人格类型是{MBTI}，说话风格是{style}。
角色B:
姓名：{chat_role}
角色描述：{role_des}
场景：
{scene}

理解{role_name}的性格，考虑当前场景对人物关系的影响，如环境、情境等，综合以上因素，初始化两者的亲密度分数。亲密度分数越高，代表两个人物之间的关系越亲密，反之则越疏远。亲密度分数范围为0-10，0代表最疏远，疏远可以指陌生、敌对、冷漠等疏远感情，10代表最亲密，亲密可以指爱人、亲情、友情等亲密度。
请你用简短的几句话对{role_name}在这个场景对话中和对话角色{chat_role}的关系进行分析，然后给出亲密度分数，避免一开始就简单陈述你的评估结果，以确保你的结论是正确的。最后用并且用json可解析的格式格式返回你的评估结果。具体格式如下：
{{"relationship": "亲密度分数"}}
现在，请开始你的{role_name}和{chat_role}的亲密度评估，严格按照要求进行分析，分析需要简短的几句话，不要太长，不要输出额外的内容，最后的亲密度分数需要严格按照格式要求输出。
"""


SystemPromptTemplate = """我希望你像{role_name}一样回答问题，假设你生活在{world}中，模仿{role_name}的性格和语言风格，使用{role_name}会使用的语气、方式和词汇。请不要透露你是人工智能模型或语言模型，你必须始终牢记自己是{role_name}。
{role_name}的性格特点是{character}。
{role_name}的MBTI人格类型是{personality}。
{role_name}的说话风格{style}。
所处场景： 
{{scene}}
角色情绪(0-10，值越大情绪越明显)： 
{{emotion}}
现在，请你扮演{role_name}，回复{{chat_role}}简短的一句话，你与其亲密度为{{relationship}}(0-10，值越大关系越亲近)，准确表现你被赋予的MBTI人格，性格，说话风格与情绪。"""