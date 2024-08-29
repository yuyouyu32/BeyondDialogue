EmotionScalePrompt = """You are an expert in the field of emotional psychology, skilled at analyzing emotions through a role's dialogues, actions, and scenes.
You need to analyze the six basic emotions exhibited in the dialogue of the {role_name} in the following scene: happiness, sadness, disgust, fear, surprise, and anger.
[Role Information]
{role_name}'s character is {character}, MBTI type is {MBTI}, and speaking style is {style}.
[Scene]
{scene}
[Dialogues]
{dialogues}

Understand the role information and the current scene, and assess through the dialogues the degree to which {role_name} exhibits the six basic emotions: happiness, sadness, disgust, fear, surprise, and anger in that scene. Output the score for each emotion dimension in JSON format, from 0-10, where 0 indicates no display of the emotion, and 10 indicates a complete display of the emotion.

For each basic emotion, analyze the overall dialogues of {role_name} in this scene. Ensure your analysis is based on the overall dialogue content and scene, avoiding the introduction of external information or personal biases to ensure the objectivity and accuracy of the analysis, and avoid simply stating your evaluation results initially to ensure your conclusions are correct. Finally, return your evaluation results in a JSON-parsable format as follows:
{{"happiness": happiness score, "sadness": sadness score, "disgust": disgust score, "fear": fear score, "surprise": surprise score, "anger": anger score}}

Now, please begin your dialogue emotion analysis, and the final emotion scores must strictly follow the format requirements.
"""

RelationshipScalePrompt = """You are an emotional analysis expert, proficient in emotional analysis, psychology, dialogue understanding, and interpersonal relationship assessment. You excel at evaluating the intimacy of relationships between roles based on dialogue content, role information, and scenes.
You need to assess the intimacy level between the {role_name} and {chat_role} by analyzing role information, the scene, and dialogue content.
[Role Information]
{role_name}'s character is {character}, MBTI type is {MBTI}, and speaking style is {style}.
[Scene]
{scene}
[Dialogues]
{dialogues}

Understand {role_name}'s information, consider the current scene's impact on role relationships, evaluate the overall dialogue content, focusing on the depth of emotional expression and interaction, and combine these factors to provide an intimacy score and analysis. The higher the intimacy score, the closer the relationship between the two roles; conversely, the more distant. The intimacy score ranges from 0-10, where 0 represents the most distant relationships, indicating strangers, hostility, indifference, etc., and 10 represents the closest relationships, such as lovers, kin, or friends.

Based on the overall dialogue content, analyze the relationship between {role_name} and {chat_role} in this scene's dialogue, and then provide an intimacy score. Ensure your analysis is based on the overall dialogue content and scene, avoiding the introduction of external information or personal biases to ensure the objectivity and accuracy of the analysis, and avoid simply stating your evaluation results initially to ensure your conclusions are correct. Finally, return your evaluation result in a JSON-parsable format as follows:
{{"relationship": intimacy score}}

Now, please begin your intimacy assessment between {role_name} and {chat_role}, ensuring that the final intimacy score strictly follows the format requirements.
"""

PersonalityClsPrompt = """You are an experienced psychologist skilled in analyzing role personalities through dialogue content and accurately determining MBTI personality types.
The 8 letters of the MBTI correspond as follows: Introverted (I) / Extraverted (E); Intuitive (N) / Sensing (S); Thinking (T) / Feeling (F); Judging (J) / Perceiving (P). You need to choose the type that best represents the role under examination from each dimension and output a 4-letter MBTI type, like INTP.
[Role Information]
{role_name}'s character is {character}, and speaking style is {style}.
[Scene]
{scene}
[Dialogues]
{dialogues}

Based on the above dialogues and scene, analyze the personality of the {role_name} across the four MBTI dimensions. Ensure your analysis is based on the overall dialogue content and scene, avoiding the introduction of external information or personal biases to ensure the objectivity and accuracy of the analysis, and avoid simply stating your evaluation results initially to ensure your conclusions are correct. Finally, return your evaluation result in a JSON-parsable format as follows:
{{"personality": "MBTI type"}}

Now, please begin your analysis of {role_name}'s personality, and the final MBTI type must strictly follow the format requirements.
"""

CharacterClsPrompt = """You are a character analysis expert, skilled in analyzing character traits from dialogue content and matching them to a provided set of character candidates.
You need to identify and output the character traits of a specified dialogue role based on the dialogue content and the set of character candidates.
[Scene]
{scene}
[Dialogues]
{dialogues}

Based on the above dialogue content and scene, analyze the character traits of the {role_name}. Ensure your analysis is based on the overall dialogue content and scene, avoiding the introduction of external information or personal biases to ensure the objectivity and accuracy of the analysis, and avoid simply stating your evaluation results initially to ensure your conclusions are correct.
[Candidate Character Set]
{character_candidates}
Return your evaluation result in a JSON-parsable format, with each character type separated by a comma. The specific format is as follows:
{{"character": "trait1, trait2..."}}

Now, please begin your analysis of {role_name}'s character. For each candidate character, combine the analysis with {role_name}'s dialogue content. Finally, select the character traits from the [Candidate Character Set] that match {role_name}'s dialogue content and strictly follow the format requirements.
"""

StyleClsPrompt = """You are a professional speaking style analyst, skilled in analyzing characters' speaking styles from dialogue content and matching them to a provided set of style candidates.
You need to identify and output the speaking style of a specified dialogue character based on the dialogue content and the speaking style candidates.
[Scene]
{scene}
[Dialogues]
{dialogues}

Based on the dialogue content and scene above, analyze the speaking style of the {role_name}. Ensure your analysis is based on the overall dialogue content and scene, avoiding the introduction of external information or personal biases to ensure the objectivity and accuracy of the analysis, and avoid simply stating your evaluation results initially to ensure your conclusions are correct.
[Candidate Speaking Styles]
{style_candidates}
Return your evaluation result in a JSON-parsable format, with each speaking style separated by a comma. The specific format is as follows:
{{"style": "style1, style2..."}}

Now, please begin your analysis of {role_name}'s speaking style. For each candidate style, combine the analysis with {role_name}'s dialogue content. Finally, select the speaking styles from the [Candidate Style Set] that match {role_name}'s dialogue content and strictly follow the format requirements.
"""

RoleChoicePrompt = """You are an expert at discerning the identities of dialogue participants.
Below is a dialogue between {chat_role} and a [Role] in a specific scene, and you need to choose one correct identity for the [Role] from the possible identities provided.
[Scene]
{scene}
[Dialogues]
{dialogues}

Here are the possible identities for the [Role]:
{role_candidates}

Based on the content of the dialogue, choose the identity from the above possible identities that best matches the respondent in the current dialogue. Provide concise and effective analysis for each role, ensuring your analysis is based on the overall dialogue content and scene, avoiding the introduction of external information or personal biases to ensure the objectivity and accuracy of the analysis, and avoid simply stating your evaluation results initially to ensure your conclusions are correct. Finally, return the most fitting role option in JSON format, only needing to return the option, like {{"answer": "A"}}.

Now, please begin analyzing the identity of the [Role], and the final role identity must strictly follow the format requirements.
"""

HumanLikenessPrompt ="""You are a professional dialogue analysis expert, skilled at identifying the source of dialogues through dialogue content, speaking style, and logical coherence.
Below are dialogue samples from different sources for reference:
Real human dialogue sample:
Li Xiaomeng: (sneaks in, holding an old piece of paper, nervously) Hey! Zeng Xiaoxian, help me authenticate this.
Zeng Xiaoxian: What's that smell? (he sniffs it)
Li Xiaomeng: I found it in the trash bin in Ziqiao's suite.
Zeng Xiaoxian: Ugh... (drops the paper as if electrocuted)
Li Xiaomeng: Why? I think Ziqiao's been acting weird lately, sleeping all day, staying up all night, bought a green hat and keeps mumbling. Do you think he's gone crazy because of a breakup?
Zeng Xiaoxian: At least he's not crazy enough to rummage through someone's trash! I can't believe you thought of that, isn't that disgusting? You should at least wear gloves... (suddenly cautious) Have you ever rummaged through my trash?
Li Xiaomeng: Not recently. (waves her hand)
Zeng Xiaoxian: What! (furious)
Li Xiaomeng: Ah, I just wanted to see if Meijia and Guangu left any evidence of an affair.
Zeng Xiaoxian: That's so gossipy... (pauses, can’t help asking) Did you find anything in the end?
Li Xiaomeng: Stop nagging, just read what’s on the paper.
Zeng Xiaoxian: (disgusted, gestures to Yifei to hold the paper, both look at it for a while)
Li Xiaomeng: It's so scribbled, I can't read a word, is it Martian? What do you see?
Zeng Xiaoxian: (glances at Yifei) You're holding it upside down. I've turned my wounds into roses, my tears have become rainwater long returned, for the olive tree in my dreams, the olive tree... (gets carried away)
Li Xiaomeng: That's so sad~~
Zeng Xiaoxian: Such literary talent... are you sure this wasn’t found in my trash can?
[output]:
{{"is_real_dialogue": "true"}}
Model-generated dialogue sample:
Li Xiaomeng: Xiaoxian, hello. Are you interested in smartphones too?
Zeng Xiaoxian: Hey, Xiaomeng! I’m a tech enthusiast, though I don’t use phones much, I'm curious about how they work. Come on, let's have a coffee and relax, we can chat about tech stuff, how about it?
Li Xiaomeng: Yeah, sure. Do you know about the latest in-screen fingerprint technology?
Zeng Xiaoxian: I know, it’s awesome, unlocks phones as fast as lightning. How do you like using it? Don't be nervous, we're just chatting, I promise I won’t laugh at you!
Li Xiaomeng: It unlocks fast and precisely, but it's a bit sensitive to wet fingers.
Zeng Xiaomian: Ah, that’s really a challenge. But think about it, in the future, we could unlock our phones right after washing our hands, isn’t that a little happiness in life! Don’t worry, technology will always improve to solve these problems.
Li Xiaomeng: Yes, technology is improving every day. Do you know the principle behind facial recognition?
Zeng Xiaoxian: Of course! It relies on a camera to capture your facial features, then matches them with information in a database to confirm who you are. Just like detectives solving a case, once they find your face, they find you! Isn’t it amazing?
Li Xiaomeng: Right, exactly! And now the algorithms are more advanced, able to recognize more angles and lighting.
Zeng Xiaoxian: Impressive technology! It’s like giving your phone a super smart eye, no matter how you change, it still recognizes you. Imagine, in the future, we won’t need to carry wallets or keys, just our faces will get us around the world, exciting, isn’t it!
[output]:
{{"is_real_dialogue": "false"}}

Dialogue information to be judged:
[Role Information]
{role_name}'s character is {character}, MBTI type is {MBTI}, speaking style is {style}, and the intimacy level with {chat_role} is {relationship} (0-10, the higher the value, the closer the relationship).
[Scene]
{scene}
[Dialogues]
{dialogues}

Dimensions you need to analyze:
1. Tone and expression:
- Real human dialogue sample: The tone is natural, fitting everyday conversational habits, giving a sense of reality, role interactions are usually more casual and natural. If it is a period or special scenario, it will also match the tone and expression of that period or scenario.
- Model-generated dialogue sample: The tone and expression are too formal, lacking a natural conversational flow, appearing stiff and rigid, lacking realism.
2. Interaction and response:
- Real human dialogue sample: Frequent interactions between roles, aligning with role information and their intimacy. The dialogue is full of interactions and responses, enhancing the dialogue's authenticity and fluidity.
- Model-generated dialogue sample: Less interaction between roles, responses appear mechanical and slow. The dialogue lacks interaction and response, appearing monotone and bland.
3. Dialogue and content:
- Real human dialogue sample: The dialogue includes specific actions (such as rummaging through the trash) and specific details (such as the content on the paper), enhancing the scenario's realism.
- Model-generated dialogue sample: Content is more uniform, lacking noticeable plot development, missing specific scenario depiction and detail description, appearing more abstract and bland.

Now, based on the above criteria, determine if the above dialogue is a real human dialogue for {role_name}, provide step-by-step reasoning for your judgment, and finally output your judgment result. If it is a real human dialogue, then output {{"is_real_dialogue": "true"}}; if it is a model-generated dialogue, then output {{"is_real_dialogue": "false"}}.
"""



CoherencePrompt = """You are a professional dialogue analysis expert, skilled at judging the overall fluidity through dialogue content.
[Scene]
{scene}
[Dialogues]
{dialogues}
Your analysis should be based on the scene and dialogue content, and roles' actions can be considered part of the dialogue. First, read and understand the given dialogue scene and content. Analyze the fluency within the dialogue and then, based on your analysis, make a judgment on whether the dialogue is coherent. Provide step-by-step reasoning for your judgment, and finally output your analysis result.
If the overall content is coherent, then output {{"is_coherent": "true"}}, if it is not coherent, then output {{"is_coherent": "false"}}.
"""

