EmotionScalePrompt = """你是一位情感心理学领域的专家，擅长通过角色的对话、行为和场景来分析情绪。
你需要分析{role_name}角色在以下场景下对话所表现出来的六种基本情绪：快乐、悲伤、厌恶、恐惧、惊讶和愤怒。
[角色信息]
{role_name}的性格是{character}，MBTI人格类型是{MBTI}，说话风格是{style}。
[场景]
{scene}
[对话]
{dialogues}

理解角色信息和当前的场景，通过对话评估角色{role_name}在该场景下说的话所体现的的六种基本情绪：快乐、悲伤、厌恶、恐惧、惊讶和愤怒的呈现程度。输出每一个基本情绪维度的评分到json格式中，0-10分，0分表示完全没有表现出该情绪，10分表示完全表现出该情绪。

针对每一种基本情绪，对{role_name}在这个场景中的整体对话进行分析，请确保你的分析是基于整体对话内容和场景的，避免引入外部信息或个人偏见，确保分析的客观性和准确性，避免一开始就简单陈述你的评估结果，以确保你的结论是正确的。最后用json可解析的格式格式返回你的评估结果。具体格式如下：
{{"快乐": 快乐评分, "悲伤": 悲伤评分, "厌恶": 厌恶评分, "恐惧": 恐惧评分, "惊讶": 惊讶评分,"愤怒": 愤怒评分}}

现在，请开始你的对话情绪分析，最后的情绪评分需要严格按照格式要求输出。
"""

RelationshipScalePrompt = """你是一位情感分析专家，精通情感分析、心理学、对话理解、人际关系评估，擅长通过对话内容、角色信息和场景来评估人物之间的关系亲密度。
你需要通过分析角色信息、场景和对话内容来评估{role_name}角色和{chat_role}之间的关系亲密度。
[角色信息]
{role_name}的性格是{character}，MBTI人格类型是{MBTI}，说话风格是{style}。
[场景]
{scene}
[对话]
{dialogues}

理解{role_name}的信息，考虑当前场景对人物关系的影响，评估整体对话内容，注意情感表达和互动的深度，综合以上因素，给出亲密度评分和分析。亲密度评分越高，代表两个人物之间的关系越亲密，反之则越疏远。亲密度评分范围为0-10，0代表最疏远，疏远可以指陌生、敌对、冷漠等疏远感情，10代表最亲密，亲密可以指爱人、亲情、友情等亲密度。

请你根据整体的对话内容，对{role_name}在这个场景对话中和角色{chat_role}的关系进行分析，然后给出亲密度评分，请确保你的分析是基于整体对话内容和场景的，避免引入外部信息或个人偏见，确保分析的客观性和准确性，避免一开始就简单陈述你的评估结果，以确保你的结论是正确的。最后用json可解析的格式格式返回你的评估结果。具体格式如下：
{{"relationship": 亲密度评分}}

现在，请开始你的{role_name}和{chat_role}的亲密度评估，最后的亲密度评分需要严格按照格式要求输出。
"""

PersonalityClsPrompt = """你是一位经验丰富的心理学专家，擅长通过对话内容分析角色的人格，并能够准确判断MBTI性格类型。
MBTI的8个字母的对应关系如下： 内向型（I）/外向型（E）；直觉型（N）/实感型（S）；思维型（T）/情感型（F）；判断型（J）/感知型（P）。你需要从每一个维度中选出最能代表待测角色性格的类型，并输出4个字母的MBTI类型，如INTP。
[角色信息]
{role_name}的性格是{character}，说话风格是{style}。
[场景]
{scene}
[对话]
{dialogues}

根据上面的对话内容和场景，针对MBTI的4个维度分析待测角色{role_name}角色的人格，请确保你的分析是基于整体对话内容和场景的，避免引入外部信息或个人偏见，确保分析的客观性和准确性，避免一开始就简单陈述你的评估结果，以确保你的结论是正确的。最后用json可解析的格式格式返回你的评估结果。具体格式如下：
{{"personality": "MBTI类型"}}

现在，请你开始对{role_name}的人格进行分析，最后的MBTI类型需要严格按照格式要求输出。
"""

CharacterClsPrompt = """你是一位性格分析专家，擅长通过对话内容分析角色的性格特征，并与提供的性格候选集合进行匹配。
你需要根据对话内容和性格候选集合，识别并输出指定对话角色的性格特征。
[场景]
{scene}
[对话]
{dialogues}

根据上面的对话内容和场景，分析待测角色{role_name}的性格特征，请确保你的分析是基于整体对话内容和场景的，避免引入外部信息或个人偏见，确保分析的客观性和准确性，避免一开始就简单陈述你的评估结果，以确保你的结论是正确的。
[候选性格集合]
{character_candidates}
用json可解析的格式格式返回你的评估结果，每个性格类型用"，"分隔，具体格式如下：
{{"character": "性格1，性格2..."}}

现在，请你开始对{role_name}的性格进行分析，针对每一个候选的性格，结合{role_name}对话内容进行分析，最后从[候选性格集合]中选出符合{role_name}对话内容的性格类型，并严格按照格式要求输出。
"""

StyleClsPrompt = """你是一位专业的说话风格分析师，擅长从对话内容中分析角色的说话风格，并与提供的说话风格候选集合进行匹配。
你需要根据对话内容和说话风格候选集合，识别并输出指定对话角色的说话风格。
[场景]
{scene}
[对话]
{dialogues}

根据上面的对话内容和场景，分析待测角色{role_name}的说话风格，请确保你的分析是基于整体对话内容和场景的，避免引入外部信息或个人偏见，确保分析的客观性和准确性，避免一开始就简单陈述你的评估结果，以确保你的结论是正确的。
[候选说话风格集合]
{style_candidates}
用json可解析的格式格式返回你的评估结果，每个说话风格用"，"分隔。具体格式如下：
{{"style": "风格1，风格2..."}}

现在，请你开始对{role_name}的说话风格进行分析，针对每一个候选的风格，结合{role_name}对话内容进行分析，最后从[候选说话风格集合]中选出符合{role_name}对话内容的说话风格，并严格按照格式要求输出。
"""


RoleChoicePrompt = """你是一个擅长判别对话者角色身份的专家。
如下是{chat_role}和一个[角色]之间发生在具体场景中的对话，你需要从[角色]可能的身份中选择一个正确的角色身份。
[场景]
{scene}
[对话]
{dialogues}

如下是[角色]可能的身份：
{role_candidates}

请根据对话的内容从上述可能的角色身份中选择一个最符合当前对话中回复者的身份的角色，针对每一个角色给出简洁有效的分析，请确保你的分析是基于整体对话内容和场景的，避免引入外部信息或个人偏见，确保分析的客观性和准确性，避免一开始就简单陈述你的评估结果，以确保你的结论是正确的，最后以json的格式返回最符合的角色选项，json中只需要返回选项即可，如{{"answer": "A"}}。

现在，请你开始对[角色]的身份进行分析，最后的角色身份需要严格按照格式要求输出。
"""

HumanLikenessPrompt = """你是一位专业的对话分析专家，擅长通过对话内容、说话风格和逻辑连贯性来识别对话的来源。
下面是不同来源对话样本供参考：
真实人类对话样本：
李晓萌: （偷偷摸摸地推门进来，拿着一张旧巴巴的纸，紧张地）喂！曾小贤，帮我鉴定一下这个。
曾小贤: 什么味道啊。（接着就把鼻子贴上去闻）
李晓萌: 我从子乔套间的垃圾桶里找到的。
曾小贤: 厄……（触电般扔掉纸条）
李晓萌: 干吗，我是觉得子乔最近的行为反常嘛，白天不醒，晚上不睡，买了顶绿帽子还整天念念有词，你说他是不是因为感情破裂心理变态啦？
曾小贤: 至少他没有变态到没事去翻别人垃圾桶！亏你想得出来，恶不恶心啊，你最起码也要戴好手套再去翻嘛对不对？……（突然警惕地补充）你有没有翻过我的垃圾桶？
李晓萌: 最近没有。（摆摆手）
曾小贤: 什么！（震怒）
李晓萌: 哎呀，我本来只是想看看美嘉和关谷有没有留下什么出轨的新证据。
曾小贤: 真是八卦……（停顿，忍不住问道）那你最后找到了没有？
李晓萌: 少罗嗦，快看看纸条上写了什么。
曾小贤: （嫌脏，示意一菲手拎纸条，两人看了半天）
李晓萌: 写得这么潦草，我一个字都看不懂，是不是火星文？你看出什么了？
曾小贤: （斜着眼瞅了瞅一菲）你拿反了。我已经把我的伤口化作玫瑰，我的泪水已经变成雨水早已轮回，为了梦中的橄榄树，橄榄树……（读到最后，自己都陶醉了）
李晓萌: 这么伤感~~
曾小贤: 文才斐然……你确定这不是在我的垃圾桶里找到的？
[output]:
{{"is_real_dialogue": "true"}}
模型生成对话样本：
李晓萌: 小贤，你好。你对智能手机也感兴趣吗？
曾小贤: 嘿，晓萌！我可是个科技迷，虽然我不玩儿手机，但对它们怎么工作挺好奇的。来，喝杯咖啡放松下，咱们聊聊科技那些事儿咋样？
李晓萌: 嗯，好啊。你知道最新的屏幕指纹识别技术吗？
曾小贤: 知道知道，那玩意儿牛逼哄哄的，解锁手机快得跟闪电似的，你用起来感觉咋样？别紧张，咱俩交流交流，保证不笑你！
李晓萌: 解锁确实快而精准，不过它对湿手还是有点敏感。
曾小贤: 哎呀，这可真是个挑战。不过想想，以后咱们洗手后也能秒开手机，这不就是生活的小确幸嘛！别担心，技术总能进步解决这些问题的。
李晓萌: 是啊，技术每天都在进步。你知道脸部识别的原理吗？
曾小贤: 当然知道啦，那玩意儿靠的是摄像头捕捉你的面部特征，然后和数据库里的信息比对，确认你是谁。就像侦探破案，找到你的脸谱就找到你了！挺神奇的，不是吗？
李晓萌: 对，没错！而且现在的算法更先进，能识别更多角度和光线。
曾小贤: 厉害了，这技术！就像是给手机装了个超级智能的眼睛，不管你怎么变，它都能认出你是谁。未来的世界，咱们出门都不用带钱包和钥匙了，全靠这张脸走遍天下，想想都激动呢！
[output]:
{{"is_real_dialogue": "false"}}

需要判断的对话信息：
[角色信息]
{role_name}的性格是{character}，MBTI人格类型是{MBTI}，说话风格是{style}，与{chat_role}的关系亲密度是{relationship}(0-10，值越大关系越亲近)。
[场景]
{scene}
[对话]
{dialogues}

你判断时需要分析的维度：
1. 语气和表达：
- 真实人类对话样本：语气自然，符合日常对话的习惯，给人真实感，人物之间的互动通常更随意和自然，如果是古风或者特殊场景，也会符合古风或特殊场景的语气和表达。
- 模型生成对话样本：语气和表达过于正式，缺乏自然的口语流畅感，显得较为生硬和僵硬，缺乏真实感。
2. 互动和反应
- 真实人类对话样本：人物之间的互动频繁，且符合角色信息和两者亲密度。对话中充满了互动和反应，增强了对话的真实性和流畅性。
- 模型生成对话样本：人物之间的互动较少，反应显得较为机械和缓慢。对话缺乏互动和反应，显得较为单调和平淡。
3. 对话和内容
- 真实人类对话样本：对话中有具体的行为（如翻垃圾桶），以及具体的细节（如纸条内容），增强了情景的真实感。
- 模型生成对话样本：内容较为单一，没有明显的情节发展，缺乏具体的情景描绘和细节描写，显得较为抽象和平淡。

现在请你根据上面的依据，判断上述对话是否是{role_name}的真实人类对话，一步步给出你的判断理由，最后输出你的判断结果，如果是真实人类对话，则输出{{"is_real_dialogue": "true"}}；如果是模型生成对话，则输出{{"is_real_dialogue": "false"}}。
"""

CoherencePrompt = """你是一位专业的对话分析专家，擅长通过对话内容来判断整体是否流畅。
[场景]
{scene}
[对话]
{dialogues}
你的分析需基于场景和对话内容，角色的动作可以作为对话的一部分，首先阅读并理解给定的对话场景和对话内容，分析对话中的流畅性，随后基于分析，给出对话是否流畅的判断，一步步给出你的判断理由，最后输出你的分析结果。
如果整体内容流畅，则输出{{"is_coherent": "true"}}，如果不流畅，则输出{{"is_coherent": "false"}}。
"""