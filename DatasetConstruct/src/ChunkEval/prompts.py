prompt_cn = """你是一位在文学和心理学领域具有深厚背景的专家，擅长从文本中分析和解读角色的性格特征及其对话表现。您的任务是按照评估步骤，帮助用户评估文本中角色{role_name}的对话性格表现效果。
分析应基于文本内容，避免引入外部信息或个人偏见，确保分析的客观性和准确性。

[角色性格]
{character}

[文本]
{chunk}

[评价标准］
体现效果（1-10）： 文本中{role_name}说的话是否体现了{role_name}的性格特征

[评价步骤］
1. 通读角色的性格描述并理解
2. 阅读并理解用户提供的文本内容。
3. 定位文本中角色说了哪些话
4. 评估文本中角色说的话对角色性格的体现程度。
角色的个性和偏好？
4. 使用给定的1-10级评分表来评定文本在多大程度上体现了{role_name}的性格特征。1表示完全没有反映角色的性格，10表示完全反映角色的性格。

首先，按照评估步骤逐步写出你对文本评估的推理，以确保你的结论是正确的，避免一开始就简单陈述你的评估结果。在最后一行上重复你的评估分数，并且用json可解析的格式{{"score": 评估分数}}格式返回你的评估结果。
"""

prompt_cn_conflict_check = """你是一位在文学和心理学领域具有深厚背景的专家，擅长从文本中分析和解读角色的性格特征及其对话表现。你的任务是根据角色描述，评估文本中角色的对话是否与其性格描述相冲突。
[角色描述]
{role_des}

[场景]
{scene}

[对话]
{dialogue}

[评价步骤]
1. 通读角色的描述并理解。
2. 阅读并理解角色的对话内容。
3. 对比对话内容和性格描述，评估是否存在冲突。
   - 如果对话内容与性格描述不符，认为存在冲突，输出1。  
   - 如果对话内容与性格描述一致，认为不存在冲突，输出0。

首先，按照评估步骤逐步写出你对对话评估的推理，以确保你的结论是正确的，避免一开始就简单陈述你的评估结果。在最后一行上重复你的评估结果，并且用json可解析的格式{{"conflict": 1/0}}格式返回你的评估结果。
"""
prompt_en = """You are an expert with a strong background in literature and psychology, skilled at analyzing and interpreting the role traits and dialogue performances of roles from texts. Your task is to help users evaluate the dialogue role performance of {role_name} according to assessment steps.
The analysis should be based on the text content, avoiding external information or personal biases to ensure the objectivity and accuracy of the analysis.

[Character Traits]
{character}

[Text]
{chunk}

[Evaluation Criteria]
Effectiveness (1-10): How well do the words spoken by {role_name} in the text reflect {role_name}'s role traits?

[Evaluation Steps]
1. Read and understand the role description.
2. Read and understand the text provided by the user.
3. Identify what the role has said in the text.
4. Assess the degree to which the role's words in the text reflect their personality traits.
5. Use the given 1-10 scale to rate how well the text reflects {role_name}'s role traits. A score of 1 indicates no reflection of the role's traits, while a score of 10 indicates a complete reflection.

First, follow the evaluation steps step-by-step to write out your reasoning for the text assessment to ensure your conclusions are accurate, avoiding a simplistic statement of your evaluation result initially. Repeat your evaluation score on the last line in a JSON-parsable format {{"score": evaluation score}} to return your evaluation result.
"""

prompt_en_conflict_check = """You are an expert in the fields of literature and psychology, skilled at analyzing and interpreting the role traits and dialogue performances in texts. Your task is to evaluate whether the dialogue of a role in the text conflicts with their described personality.

[Role Description]
{role_des}

[Scene]
{scene}

[Dialogue]
{dialogue}

[Evaluation Steps]
1. Read and understand the role description.
2. Read and comprehend the dialogue of the role.
3. Compare the dialogue to the role description to assess for any conflicts.
   - If the dialogue does not align with the role description, it is considered a conflict and output 1.
   - If the dialogue aligns with the role description, it is considered to have no conflict and output 0.

First, follow the evaluation steps to gradually write out your reasoning for the dialogue assessment to ensure your conclusion is correct, avoiding premature simple statements of your evaluation result. On the last line, repeat your evaluation result and return it in a JSON-parsable format with {"conflict": 1/0}.
"""