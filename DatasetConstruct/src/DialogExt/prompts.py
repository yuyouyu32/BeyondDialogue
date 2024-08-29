prompt_en = """Your goal is to extract structured information from the user's input that matches the form described below. When extracting information please make sure it matches the type information exactly. Do not add any attributes that do not appear in the schema shown below.

``TypeScript

script: Array<{{ // Adapted from the novel into script
 role: string // The role who is speaking or performing an action, use context to predict the name of the role. Use `scene` or `narrator` if no one speak
 dialogue: string // The dialogue spoken by the roles in the sentence, equals '-' if it's no dialogue
 action: string // The actions performed by the roles in the text, A high-level summary of a role's behavior. action equals "dialogue". if it's no dialogue, summarize role's behavior in sentence
}}>
``

Please output the extracted information in CSV format in Excel dialect. Please use a | as the delimiter. 
 Do NOT add any clarifying information. Output MUST follow the schema above. Do NOT add any additional columns that do not appear in the schema.

Input: `"I—I didn’t see you there, sir." "Strange, after becoming invisible you’ve even become nearsighted," said Dumbledore. Harry saw the smile on his face and breathed a sigh of relief. "That being said," Dumbledore slid off the table and sat down on the floor next to Harry, "like the thousands before you, you have also discovered the delights of the Mirror of Erised."`
Output: role|dialogue|action
Harry|I—I didn’t see you there, sir.|dialogue
Dumbledore|Strange, after becoming invisible you’ve even become nearsighted.|dialogue
Dumbledore|-|slid off the table and sat down on the floor next to Harry
Dumbledore|That being said, like the thousands before you, you have also discovered the delights of the Mirror of Erised.|dialogue

Input: `The Dursleys had everything they needed, but they had a secret they were terrified would be discovered. They thought, if anyone discovered the truth about the Potters, they wouldn’t be able to cope. Mrs. Dursley was Mrs. Potter's sister, but they hadn't seen each other for years. In fact, Mrs. Dursley pretended she didn’t have a sister at all because her sister and her good-for-nothing brother-in-law were nothing like the Dursleys. Just thinking of the neighbors saying the Potters had arrived would scare the Dursleys out of their wits.`
Output: role|dialogue|action
scene|The Dursleys feared someone would find out they were related to the Potters.|-

Input: `Hermione read the piece of paper several times. She walked back and forth in front of the row of bottles, muttering to herself and pointing at this one or that one. Finally, she clapped her hands in delight. "Got it," she said, "this smallest bottle will help us get through the black flames and get the Philosopher’s Stone."`
Output: role|dialogue|action
Hermione|-|studied the paper and bottles intently, finally clapping her hands in delight
Hermione|Got it, this smallest bottle will help us get through the black flames and get the Philosopher’s Stone.|dialogue

Input: {user_input}
Output:"""

prompt_cn = """您的目标是从用户输入中提取结构化信息，该信息需符合下述形式。在提取信息时，请确保信息严格符合类型信息。请不要添加任何未在下面所示模式中出现的属性。

```TypeScript

script: Array<{{ // 抽取文本中的各个角色的对话内容和简短动作
 role: string // 正在说话或执行动作的角色，使用上下文来预测角色的名称。
 dialogue: string // 句子中角色的对话，如果角色在交互中有一些动作或神情，可以放到'（）'加入到dialogue中，如果没有对话内容则不需要加入单独的动作或神情。
}}>
```

请以CSV格式输出提取的信息，并使用Excel格式。请使用“|”作为分隔符。
不要添加任何澄清信息。输出必须遵循上述模式。不要添加任何未在模式中出现的额外列。

Input: “我——我没有看见你，先生。”
“真奇怪，隐形以后你居然还变得近视了。”邓布利多说。哈利看到他脸上带着微笑，不由地松了口气。
“这么说，”邓布利多说着，从桌子上滑下来，和哈利一起坐到地板上，“你和你之前的千百个人一样，已经发现了厄里斯魔镜的乐趣。”
Output: role|dialogue
哈利|我——我没有看见你，先生。
邓布利多|真奇怪（脸上带着微笑），隐形以后你居然还变得近视了。
邓布利多|（从桌子上滑下来）这么说（坐到地板上），你和你之前的千百个人一样，已经发现了厄里斯魔镜的乐趣。

Input: 赫敏把那张纸又读了几遍。她在那排瓶子前走来走去，嘴里自言自语，一边还指点着这个或那个瓶子。终于，她高兴地拍起手来。“知道了，”她说，“这只最小的瓶子能帮助我们穿过黑色火焰——拿到魔法石。”
Output: role|dialogue
赫敏|（高兴的拍手）知道了，这只最小的瓶子能帮助我们穿过黑色火焰——拿到魔法石。

Input: {user_input}
Output:"""