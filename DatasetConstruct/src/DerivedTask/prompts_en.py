EmotionPrompt = """You are an expert in the field of emotional psychology, skilled at analyzing emotions through a role's dialogues, actions, and scenes. The analysis of role's emotions should be based on their dialogues, actions, and the scene they are in, avoiding external information or personal biases to ensure the objectivity and accuracy of the analysis.
You need to analyze the six basic emotions: happiness, sadness, disgust, fear, surprise, and anger for {role_name} in a specific scene.
[Role Information]
{role_name}'s character is {character}, MBTI type is {MBTI}, and speaking style is {style}.
[Scene]
{scene}
[Dialogues]
{dialogues}

Understand the role's information and the current scene, and assess through the dialogues the degree to which {role_name} exhibits the six basic emotions: happiness, sadness, disgust, fear, surprise, and anger. Output the score for each emotion dimension in JSON format, from 0-10, where 0 indicates no display of the emotion, and 10 indicates a complete display of the emotion.

Please analyze the emotions of {role_name} in this scene through a few brief sentences, avoiding a simplistic statement of your evaluation results initially, to ensure your conclusions are accurate. Finally, return your evaluation results in a JSON-parsable format as follows:
{{"happiness": happiness score, "sadness": sadness score, "disgust": disgust score, "fear": fear score, "surprise": surprise score, "anger": anger score}}

Now, please begin your dialogue emotion analysis, strictly adhering to the requirements. The analysis should be brief and avoid lengthy descriptions or additional content. The final emotional scores must strictly follow the format requirements.
"""

RelationshipPrompt = """You are an expert in emotional analysis, specializing in sentiment analysis, psychology, dialogue comprehension, and interpersonal relationship assessment. You excel in assessing the intimacy of relationships between roles based on their dialogue content, role's information, and scenes.
You need to analyze the intimacy of the relationship between {role_name} and {target_name} by assessing role's information, scenes, and dialogue content.
[Role Information]
{role_name}'s character is {character}, MBTI type is {MBTI}, and speaking style is {style}.
[Scene]
{scene}
[Dialogues]
{dialogues}

Understand the information of {role_name}, consider the impact of the current scene on the relationship, such as the environment and context, evaluate the dialogue content, pay attention to the depth of emotional expression and interaction, and combine these factors to provide an intimacy score and analysis. The higher the intimacy score, the closer the relationship between the two roles; conversely, the more distant. The intimacy score ranges from 0-10, where 0 represents the most distant (which could indicate strangers, hostility, indifference), and 10 represents the closest (which could indicate lovers, kinship, friendship).

Please analyze the relationship between {role_name} and {target_name} in this scene's dialogue in a few brief sentences, then provide an intimacy score, avoiding a simplistic statement of your evaluation results initially to ensure your conclusions are accurate. Finally, return your evaluation results in a JSON-parsable format as follows:
{{"relationship": intimacy score}}

Now, please begin your intimacy assessment between {role_name} and {target_name}, strictly adhering to the requirements. The analysis should be brief and avoid lengthy descriptions or additional content. The final intimacy score must strictly follow the format requirements.
"""

PersonalityClsPrompt = """You are an experienced psychologist skilled in analyzing role's personalities through dialogue content and accurately determining MBTI personality types.
The 8 letters of the MBTI correspond as follows: Introverted (I) / Extraverted (E); Intuitive (N) / Sensing (S); Thinking (T) / Feeling (F); Judging (J) / Perceiving (P). You need to choose the type that best represents the role under examination from each dimension and output a 4-letter MBTI type, like INTP.
[Role Information]
{role_name}'s character is {character}, and speaking style is {style}.
[Scene]
{scene}
[Dialogues]
{dialogues}

Based on the above dialogues and scene, analyze the personality of the role {role_name} across the four MBTI dimensions. Ensure your analysis is based on the overall dialogue content and scene, avoiding the introduction of external information or personal biases to ensure the objectivity and accuracy of the analysis, and avoid simply stating your evaluation results initially to ensure your conclusions are correct. Finally, return your evaluation result in a JSON-parsable format as follows:
{{"personality": "MBTI type"}}

Now, please begin your analysis of {role_name}'s personality, and the final MBTI type must strictly follow the format requirements.
"""

CharacterClsPrompt = """You are a character analysis expert, skilled in analyzing character traits from dialogue content and matching them to a provided set of character candidates.
You need to identify and output the character traits of a specified dialogue role based on the dialogue content and the set of character traits candidates.
[Scene]
{scene}
[Dialogues]
{dialogues}

Based on the dialogue content and scene above, analyze the character traits of the {role_name}. Ensure your analysis is based on the overall dialogue content and scene, avoiding the introduction of external information or personal biases to ensure the objectivity and accuracy of the analysis, and avoid simply stating your evaluation results initially to ensure your conclusions are correct.
[Candidate Character Set]
{character_candidates}
Return your evaluation result in a JSON-parsable format, with each character type separated by a comma. The specific format is as follows:
{{"character": "trait1, trait2..."}}

Now, please begin your analysis of {role_name}'s character. For each candidate character, combine the analysis with {role_name}'s dialogue content. Finally, select the character traits from the [Candidate Character Set] that match {role_name}'s dialogue content and strictly follow the format requirements.
"""

StyleClsPrompt = """You are a professional speaking style analyst, skilled in analyzing roles' speaking styles from dialogue content and matching them to a provided set of style candidates.
You need to identify and output the speaking style of a specified dialogue role based on the dialogue content and the speaking style candidates.
[Scene]
{scene}
[Dialogues]
{dialogues}

Based on the dialogue content and scene above, analyze the speaking style of the {role_name}. Ensure your analysis is based on the overall dialogue content and scene, avoiding the introduction of external information or personal biases to ensure the objectivity and accuracy of the analysis and avoid simply stating your evaluation results initially to ensure your conclusions are correct.
[Candidate Speaking Styles]
{style_candidates}
Return your evaluation result in a JSON-parsable format, with each speaking style separated by a comma. The specific format is as follows:
{{"style": "style1, style2..."}}

Now, please begin your analysis of {role_name}'s speaking style. For each candidate style, combine the analysis with {role_name}'s dialogue content. Finally, select the speaking styles from the [Candidate Speaking Styles] that match {role_name}'s dialogue content and strictly follow the format requirements.
"""

