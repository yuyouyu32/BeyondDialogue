import matplotlib.pyplot as plt
import numpy as np
import json

def draw_pie(verb_nouns, name):
    verbs = list(verb_nouns.keys())
    # 计算每个动词的总值
    verb_sums = {verb: sum(values.values()) for verb, values in verb_nouns.items()}

    # 设置半径
    inner_radius = 0.5
    outer_radius = 1.0

    # 创建图和轴
    fig, ax = plt.subplots()

    # 内圈饼图（动词）
    inner_sizes = [verb_sums[verb] for verb in verbs]
    inner_labels = [verb for verb in verbs]
    inner_colors = plt.cm.tab20c(range(len(verbs)))
    inner_wedges, _ = ax.pie(inner_sizes, radius=inner_radius, colors=inner_colors, wedgeprops=dict(width=0.5, edgecolor='w'))

    # 外圈饼图（名词）
    outer_sizes = [value for values in verb_nouns.values() for value in values.values()]
    outer_labels = [noun for values in verb_nouns.values() for noun in values.keys()]
    outer_colors = [inner_colors[verbs.index(verb)] for verb in verbs for _ in verb_nouns[verb]]
    outer_wedges, _ = ax.pie(outer_sizes, radius=outer_radius, colors=outer_colors, wedgeprops=dict(width=0.5, edgecolor='w', alpha=0.7))

    # 调整内圈饼图标签的文本，使其在扇形内部
    for i, wedge in enumerate(inner_wedges):
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = 0.25 * np.cos(np.radians(angle))
        y = 0.25 * np.sin(np.radians(angle))
        font_size = min(max(inner_sizes[i] / 3, 4),8)  # Adjust font size based on pie size
        rotation = angle - 180 if 90 <= angle <= 270 else angle
        # 设置font的字体为Times New Roman
        
        ax.text(x, y, inner_labels[i], rotation=rotation, ha='center', va='center', fontsize=font_size, fontname='DejaVu Serif')

    # 调整外圈饼图标签的文本，使其在扇形内部
    start_index = 0
    for i, wedge in enumerate(inner_wedges):
        num_nouns = len(verb_nouns[verbs[i]])
        end_index = start_index + num_nouns
        for j in range(start_index, end_index):
            outer_wedge = outer_wedges[j]
            angle = (outer_wedge.theta2 + outer_wedge.theta1) / 2
            x = 0.75 * np.cos(np.radians(angle))
            y = 0.75 * np.sin(np.radians(angle))
            font_size = min(max(outer_sizes[j] / 1, 3), 7)
            rotation = angle - 180 if 90 <= angle <= 270 else angle
            ax.text(x, y, outer_labels[j], rotation=rotation, ha='center', va='center', fontsize=font_size, fontname='DejaVu Serif')
        start_index = end_index

    # 调整纵横比以保持饼图为圆形
    ax.axis('equal')

    # 显示图
    plt.savefig(f'../figures/{name}.pdf', dpi=500)

# python -m DatasetSta.v_n_pie
if __name__ == '__main__':
    v_b_path = "../data/verb_noun_pairs_en.json"
    with open(v_b_path, 'r') as f:
        verb_nouns = json.load(f)
    
    verb_nouns = dict(list(verb_nouns.items())[:20])
    draw_pie(verb_nouns, "verb_noun_instruction_en")