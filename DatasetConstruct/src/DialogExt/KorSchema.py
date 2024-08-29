from kor.nodes import Object, Text
from langchain.prompts import PromptTemplate

schema_cn = Object(
    id="script",
    description="抽取文本中的各个角色的对话内容和简短动作",
    attributes=[
        Text(
            id="role",
            description="正在说话或执行动作的角色，使用上下文来预测角色的名称。",
        ),
        Text(
            id="dialogue",
            description="句子中角色的对话，如果角色在对话中采取了一些简短的动作，可以放到'（）'加入到dialogue中，如没有对话内容则不需要加入单独的动作。",
        )
    ],
    examples=[
        (
            '''“我——我没有看见你，先生。”
“真奇怪，隐形以后你居然还变得近视了。”邓布利多说。哈利看到他脸上带着微笑，不由地松了口气。
“这么说，”邓布利多说着，从桌子上滑下来，和哈利一起坐到地板上，“你和你之前的千百个人一样，已经发现了厄里斯魔镜的乐趣。”''',
            [
                {"role": "哈利", "dialogue": "我——我没有看见你，先生。",},
                {"role": "邓布利多", "dialogue": "真奇怪（脸上带微笑），隐形以后你居然还变得近视了。",},
                {"role": "邓布利多", "dialogue": "（从桌子上滑下来）这么说（坐到地板上），你和你之前的千百个人一样，已经发现了厄里斯魔镜的乐趣。"}
            ],
        ),
        (
            '''赫敏把那张纸又读了几遍。她在那排瓶子前走来走去，嘴里自言自语，一边还指点着这个或那个瓶子。终于，她高兴地拍起手来。“知道了，”她说，“这只最小的瓶子能帮助我们穿过黑色火焰——拿到魔法石。”''',
            [
                {"role": "赫敏", "dialogue": "（高兴的拍手）知道了，这只最小的瓶子能帮助我们穿过黑色火焰——拿到魔法石。"}
            ],
        )
    ],
    many=True,
)

instruction_template_cn = PromptTemplate(
    input_variables=[],
    template=(
        "你的目标是从用户的Input中提取结构化信息，Output遵循以下的规范：\n"
        """"""
        """1. 输出格式为role|dialogue|action，其中，role为正在讲话或执行动作的角色，dialogue为角色在句子中说的对话，action为角色在文本中执行的动作，总结一个角色的行为，如果是句子中的对话，则action等于"对话"或"独白"。
2. 在提取信息时，请确保它完全匹配信息类型。请不要添加任何不在下面显示的模式中出现的属性。
3. 请将提取的信息以 CSV 格式用 Excel 语言输出。请使用 | 作为分隔符。
4. 不要添加任何说明信息，输出必须遵循上述模式，不要添加模式中未出现的任何额外列。\n"""
        "以下是两个例子："
    ),
)


schema_en = Object(
    id="script",
    description="Adapted from the novel into script",
    attributes=[
        Text(
            id="role",
            description="The character who is speaking or performing an action, use context to predict the name of the role. Use `scene` or `narrator` if no one speak",
        ),
        Text(
            id="dialogue",
            description="The dialogue spoken by the characters in the sentence, equals '-' if it's no dialogue",
        ),
        Text(
            id="action",
            description='''The actions performed by the characters in the text, A high-level summary of a character's behavior. action equals "dialogue". if it's no dialogue, summarize role's behavior in sentence''',
        )
    ],
    examples=[
        (
            '''“我——我没有看见你，先生。”
“真奇怪，隐形以后你居然还变得近视了。”邓布利多说。哈利看到他脸上带着微笑，不由地松了口气。
“这么说，”邓布利多说着，从桌子上滑下来，和哈利一起坐到地板上，“你和你之前的千百个人一样，已经发现了厄里斯魔镜的乐趣。”''',
            [
                {"role": "哈利", "dialogue": "我——我没有看见你，先生。","action":"dialogue"},
                {"role": "邓布利多", "dialogue": "真奇怪，隐形以后你居然还变得近视了。","action":"dialogue"},
                {"role": "邓布利多", "dialogue": "-", "action":"从桌子上滑下来，和哈利一起坐到地板上"},
                {"role": "邓布利多", "dialogue": "这么说，你和你之前的千百个人一样，已经发现了厄里斯魔镜的乐趣。","action":"dialogue"},
            ],
        ),
        (
            '''德思礼一家什么都不缺，但他们拥有一个秘密，他们最害怕的就是这秘密会被人发现。他们想，一旦有人发现波特一家的事，他们会承受不住的。波持太太是德思礼太太的妹妹，不过她们已经有好几年不见面了。实际上，德思礼太太佯装自己根本没有这么个妹妹，因为她妹妹和她那一无是处的妹夫与德思礼一家的为人处世完全不一样。一想到邻居们会说波特夫妇来到了，德思礼夫妇会吓得胆战心惊。''',
            [
                {"role": "scene", "dialogue": "德思礼一家害怕有人知道他们是波特一家的亲戚。","action":"-"},
            ],
        ),
        (
            '''赫敏把那张纸又读了几遍。她在那排瓶子前走来走去，嘴里自言自语，一边还指点着这个或那个瓶子。终于，她高兴地拍起手来。“知道了，”她说，“这只最小的瓶子能帮助我们穿过黑色火焰——拿到魔法石。”''',
            [
                {"role": "赫敏", "dialogue": "-", "action":"仔细研究了纸和瓶子，终于高兴地拍起手来"},
                {"role": "赫敏", "dialogue": "知道了，这只最小的瓶子能帮助我们穿过黑色火焰——拿到魔法石。","action":"dialogue"},
            ],
        )
    ],
    many=True,
)