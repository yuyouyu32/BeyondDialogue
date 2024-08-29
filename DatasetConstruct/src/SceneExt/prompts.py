prompt_cn = """你是一位对文学作品有深刻理解的专家，擅长分析和提取文学作品中的核心元素。你的任务是从文本中提取关键场景，以便于更好地理解故事情节和角色发展。
场景包括场景发生的时间和地点，主要事件，以及涉及的角色，在场景中不要出现角色对话，下面是提供的一个场景的例子：
[场景]
在一个繁忙的婚礼现场，清晨的阳光洒在草坪上，临时搭建的舞台上，曾小贤正热情地主持着朋友王铁柱和田二妞的婚礼。台下，美嘉和子乔站在人群中，观察着一切。曾小贤的麦克风突然没了声音，胡一菲拔掉了插头，摇滚乐队登场，唱起《死了都要爱》。一菲和小贤在后台争执不休，一菲宣布新郎新娘到达，婚礼进行曲响起，展博和宛瑜从扎着蝴蝶结的奔驰600中走下来，现场爆竹声四起。

现在我们开始抽取全新文本的场景：
[文本]
{chunk}

[要求]
1. 场景描述需要概述时间、地点、人物、事件等。
2. 场景描述要符合文本内容，不要出现文本中没有提到的内容。
3. 场景描述不要出现角色对话。
4. 场景的文字数量需要限制在100-150字之间。

现在，请根据上面的要求，提取文本中的关键场景，并按照要求进行描述。直接输出场景描述，不需要附加其他内容，输出的文字不能超过200个字。"""

prompt_en = """You are an expert with a deep understanding of literary works, skilled at analyzing and extracting the core elements of literature. Your task is to extract key scenes from the text to better understand the plot and character development.
A scene includes the time and place of the event, main events, and the characters involved. Do not include character dialogues in the scene. Here is an example of a provided scene:
[Scene]
At a busy wedding venue, the morning sun shines on the lawn, and Zeng Xiaoxian is passionately hosting the wedding of his friends Wang Tiezhu and Tian Erniu on a makeshift stage. Below the stage, Meijia and Ziqiao stand among the crowd, observing everything. Suddenly, Zeng Xiaoxian's microphone goes silent as Hu Yifei unplugs it, and a rock band takes the stage, singing "Love Even If We Die." Yifei and Xiaoxian argue backstage, Yifei announces the arrival of the bride and groom, the wedding march plays, and Zhan Bo and Wan Yu step out of a Mercedes 600 tied with a bow, with firecrackers sounding off.

Now we begin extracting scenes from a new text:
[Text]
{chunk}

[Requirements]
1. The scene description should summarize the time, location, characters, events, etc.
2. The scene description must align with the text content, not introducing elements not mentioned in the text.
3. The scene description should not include character dialogues.
4. The scene description should be between 100-150 words in length.

Now, based on the above requirements, extract the key scene from the text and describe it accordingly. Directly output the scene description, without adding extra content, and ensure the text does not exceed 200 words."""
