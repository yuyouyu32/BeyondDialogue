regen_prompt_cn = """您是一位擅长从文本中分析和提取关键信息的场景分析专家。你的任务是能够准确识别对话中的线索并重构场景，同时检查对话在重构的场景中是否连贯通畅。
- 重构的场景包括场景发生的时间和地点，主要事件，以及涉及的角色，在场景中不要出现角色对话。
- 对话连贯包含发言者之间的互动在场景、主题、逻辑等方面相互呼应，对话流畅、一致的交流过程。

下面是我提供的的参考场景，你需要识别出我提供的对话在场景中所处的场景，并重构这个场景的描述：
[场景]
{scene}

[对话]
{dialogue}

现在请根据上面的要求，重构对话所处的子场景，并按照要求进行描述，最后根据生成的子场景，检查对话是否连贯通畅。你可以简短分析对话所处的场景和其是否连贯，最后用json可解析的格式格式返回你的评估结果。具体格式如下：
{{"scene": "重构的场景描述", "coherence": 1/0}}
其中，"coherence"为1表示对话和场景连贯通畅，为0表示对话和场景不连贯通畅。   

现在，请开始你的场景重构，严格按照评估步骤进行分析，场景描述的不得超过150个字，场景描述和对话是否连贯需要严格按照格式要求输出。"""

regen_prompt_en = """You are an expert in scene analysis, skilled at analyzing and extracting key information from texts. Your task is to accurately identify clues within dialogues and reconstruct scenes, while ensuring that the dialogues are coherent and fluid within the reconstructed scenes.
- The reconstructed scene should include the time and place of the event, main events, and the characters involved, without including character dialogues.
- Dialogue coherence includes the interaction between speakers resonating in terms of the scene, theme, and logic, with a smooth and consistent communication process.

Here is a reference scene I provide. You need to identify the scene context of the provided dialogue and reconstruct its description:
[Scene]
{scene}

[Dialogue]
{dialogue}

Now, based on the above requirements, reconstruct the sub-scene where the dialogue takes place, and describe it accordingly. Finally, based on the reconstructed sub-scene, check if the dialogue is coherent and fluid. You may briefly analyze the scene context and its coherence, then return your evaluation result in a JSON-parsable format as follows:
{{"scene": "reconstructed scene description", "coherence": 1/0}}
Where "coherence" of 1 indicates the dialogue is coherent and fluid with the scene, and 0 indicates the dialogue is not coherent with the scene.

Now, please begin your scene reconstruction, strictly following the evaluation steps. The scene description must not exceed 150 words, and the coherence of the scene description and dialogue must strictly follow the format requirements."""
