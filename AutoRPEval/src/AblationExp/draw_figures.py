import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
plt.rcParams['font.family'] = 'Times New Roman'

def read_score_results(file_path):
    scores_df = pd.read_excel(file_path)
    # 将第一列设为索引
    scores_df.set_index(scores_df.columns[0], inplace=True)

    # 将DataFrame转换为字典
    data_dict = scores_df.to_dict(orient='index')
    return data_dict

def draw_radar_figures_one(data):
    # Extract labels
    labels = list(data['All'].keys())

    # Extract data and convert to float
    def parse_value(value):
        return float(value.split(' ± ')[0])

    parsed_data = {k: {k1: parse_value(v1) for k1, v1 in v.items()} for k, v in data.items()}

    for key, values in parsed_data.items():
        values['emotion'] = 100 - values['emotion']
        values['relationship'] = 100 - values['relationship']

    # Normalize data by dividing each value by the maximum value for its dimension
    max_values = {dim: max([v[dim] for v in parsed_data.values()]) for dim in labels}

    normalized_data = {}
    for key, values in parsed_data.items():
        normalized_data[key] = {dim: value / (max_values[dim] + 0.1) for dim, value in values.items()}

    # Number of variables
    num_vars = len(labels)

    # Compute angle of each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    # Prepare data for plotting
    normalized_values = {key: list(values.values()) + [list(values.values())[0]] for key, values in normalized_data.items()}

    # Choose a color palette
    colors = ['#1f77b4',
    '#ff7f0e',
    '#2ca02c',
    '#e377c2',
    '#9467bd',
    #  '#8c564b',
    '#d62728',
    #  '#7f7f7f',
    #  '#bcbd22',
    #  '#17becf'
    ]

    fig = plt.figure(figsize=(10, 6), dpi=200)

    ax = plt.subplot(111, polar=True)

    # Plot each group
    for color, (key, values) in zip(colors, normalized_values.items()):
        if key != 'All':
            key = key.split(' ')[0] + ' ' + key.split(' ')[1][:4].capitalize() + '.'
        ax.plot(angles, values, label=key, color=color, alpha=0.5)
        ax.fill(angles, values, color=color, alpha=0.15)

    # Set the range for each axis
    ax.set_ylim(0.92, 1)

    # Draw solid gray internal gridlines with alpha of 0.7
    for j in np.linspace(0.92, 1, 5):
        ax.plot(angles, [j]*len(angles), '-', lw=0.5, color='gray', alpha=0.8)

    # Draw one axe per variable and add labels
    ax.set_xticks(angles[:-1])
    # Move x-axis labels away from the axis
    label_map = {
        'character': 'Char.',
        'style': 'Styl.',
        'emotion': 'Emo.',
        'relationship': 'Rel.',
        'personality': 'Pers.',
        'average_score': 'Avg. Score'
    }
    ax.set_xticklabels([label_map[label] for label in labels], fontsize=10, fontstyle='italic')
    ax.tick_params(axis='x', pad=3)

    # Hide the outer frame and circular gridlines
    ax.spines['polar'].set_visible(False)
    ax.grid(False)

    # Hide the y-axis labels
    ax.set_yticklabels([])

    # Add a legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.2))

    # Add actual value labels for the axes
    for angle, label in zip(angles[:-1], labels):
        label_min = min([v[label] for v in parsed_data.values()])
        label_max = max([v[label] for v in parsed_data.values()])
        ax.text(angle, 0.945, f'{(label_max + 0.1) * 0.94:.1f}', size=8, horizontalalignment='center', verticalalignment='center', color='black', alpha=0.8)
        ax.text(angle, 0.965, f'{(label_max + 0.1) * 0.96:.1f}', size=8, horizontalalignment='center', verticalalignment='center', color='black', alpha=0.8)
        ax.text(angle, 0.995, f'{label_max + 0.1:.1f}', size=8, horizontalalignment='center', verticalalignment='center', color='black', alpha=0.8)

    plt.savefig('../ablation_results/radar_score.pdf', dpi=500, bbox_inches='tight')


def draw_radar_figures(data):
    # Extract labels
    labels = list(data['All'].keys())

    # Extract data and convert to float
    def parse_value(value):
        return float(value.split(' ± ')[0])

    parsed_data = {k: {k1: parse_value(v1) for k1, v1 in v.items()} for k, v in data.items()}

    for key, values in parsed_data.items():
        values['emotion'] = 100 - values['emotion']
        values['relationship'] = 100 - values['relationship']

    # Normalize data by dividing each value by the maximum value for its dimension
    max_values = {dim: max([v[dim] for v in parsed_data.values()]) for dim in labels}

    normalized_data = {}
    for key, values in parsed_data.items():
        normalized_data[key] = {dim: value / (max_values[dim] + 0.1) for dim, value in values.items()}

    # Number of variables
    num_vars = len(labels)

    # Compute angle of each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    # Prepare data for plotting
    normalized_values = {key: list(values.values()) + [list(values.values())[0]] for key, values in normalized_data.items()}

    # Choose a color palette
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#e377c2', '#9467bd', '#d62728']

    # Group assignments by index
    indices = list(normalized_data.keys())
    group1 = [indices[i] for i in [0, 1, 4, 5]]
    group2 = [indices[i] for i in [2, 3, 5]]

    def plot_radar(group, group_name):
        fig = plt.figure(figsize=(10, 6), dpi=200)
        ax = plt.subplot(111, polar=True)
        if group_name == 'group1':
            group_colors = [colors[i] for i in [0, 1, 2, 5]]
        else:
            group_colors = [colors[i] for i in [3, 4, 5]]
        # Plot each group
        for color, key in zip(group_colors, group):
            values = normalized_values[key]
            if key != 'All':
                key = key.split(' ')[0] + ' ' + key.split(' ')[1][:4].capitalize() + '.'
            ax.plot(angles, values, label=key, color=color, alpha=0.5)
            ax.fill(angles, values, color=color, alpha=0.15)

        # Set the range for each axis
        ax.set_ylim(0.92, 1)

        # Draw solid gray internal gridlines with alpha of 0.7
        for j in np.linspace(0.92, 1, 5):
            ax.plot(angles, [j]*len(angles), '-', lw=0.5, color='gray', alpha=0.8)

        # Draw one axe per variable and add labels
        ax.set_xticks(angles[:-1])
        # Move x-axis labels away from the axis
        label_map = {
            'character': 'Char.',
            'style': 'Styl.',
            'emotion': 'Emo.',
            'relationship': 'Rel.',
            'personality': 'Pers.',
            'average_score': 'Avg. Score'
        }
        ax.set_xticklabels([label_map[label] for label in labels], fontsize=10, fontstyle='italic', fontweight='bold')
        ax.tick_params(axis='x', pad=3)

        # Hide the outer frame and circular gridlines
        ax.spines['polar'].set_visible(False)
        ax.grid(False)

        # Hide the y-axis labels
        ax.set_yticklabels([])

        # Add a legend
        # ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.2))
        legend_elements = []
        for color, key in zip(group_colors, group):
            if key != 'All':
                key = key.split(' ')[0] + ' ' + key.split(' ')[1][:4].capitalize() + '.'
            legend_elements.append(Patch(facecolor=color, edgecolor=color, label=key, alpha=0.15, lw=2))
        
        ax.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=4, handlelength=2, handletextpad=1, frameon=False, prop={'weight': 'bold'})
        # Add actual value labels for the axes
        for angle, label in zip(angles[:-1], labels):
            label_min = min([v[label] for v in parsed_data.values()])
            label_max = max([v[label] for v in parsed_data.values()])
            ax.text(angle, 0.945, f'{(label_max + 0.1) * 0.94:.1f}', size=8, horizontalalignment='center', verticalalignment='center', color='black', alpha=0.8)
            ax.text(angle, 0.965, f'{(label_max + 0.1) * 0.96:.1f}', size=8, horizontalalignment='center', verticalalignment='center', color='black', alpha=0.8)
            ax.text(angle, 0.995, f'{label_max + 0.1:.1f}', size=8, horizontalalignment='center', verticalalignment='center', color='black', alpha=0.8)

        plt.savefig(f'../ablation_results/radar_score_{group_name}.pdf', dpi=500, bbox_inches='tight')

    # Plot each group
    plot_radar(group1, "group1")
    plot_radar(group2, "group2")

def draw_single_figures(data_dict):
    categories = [key.split(' ')[1].strip() for key in data_dict.keys() if key != 'All']
    all_values = [float(data_dict['All'][category].split("±")[0]) for category in categories]
    without_values  = [float(data_dict[f'w/o {category}'][category].split("±")[0]) for category in categories]
    # 把category为emotion和relationship的值变为1 - value
    for i, category in enumerate(categories):
        if category in ['emotion', 'relationship']:
            all_values[i] = 100 - all_values[i]
            without_values[i] = 100 - without_values[i]

    for index in range(len(categories)):
        categories[index] = categories[index].capitalize()
    # 定义柱状图的位置
    x = np.arange(len(categories))
    width = 0.21

    # 绘图
    fig, ax = plt.subplots(figsize=(8, 6))

    # 绘制柱状图
    bars1 = ax.bar(x - width/1.8, all_values, width, label='All', color='#4865A9', edgecolor='#4865A9', capsize=4, alpha=0.6)
    bars2 = ax.bar(x + width/1.8, without_values, width, label='w/o', color='#EF8A43', edgecolor='#EF8A43', capsize=4, alpha=0.6)

    # 设置x轴标签和y轴标签
    ax.set_xlabel('')
    ax.set_ylabel('Scores of Various Dimensions', fontdict={'fontsize': 20, 'fontweight': 'bold'})

    # 设置x轴刻度
    ax.set_xticks(x)
    ax.set_xticklabels(categories)

    # 隐藏x轴和y轴的轴线，但保留标签
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_alpha(0.3)

    # 设置y轴范围
    ax.set_ylim(60, 90)

    # 删除x轴刻度线
    ax.tick_params(axis='x', length=0)
    ax.tick_params(axis='y', length=0)
    ax.set_xticklabels(categories, fontstyle='italic')
    # 把x轴上的刻度字体变大，变粗
    for label in ax.get_xticklabels():
        label.set_fontsize(20)
        label.set_fontweight('bold')
    # 把y轴上的刻度字体变大，变粗
    for label in ax.get_yticklabels():
        label.set_fontsize(20)
        label.set_fontweight
    # 把y轴上的label变大， 加粗
    # 在柱子上方添加标签
    for i, bar in enumerate(bars1):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'ALL', ha='center', va='bottom', fontsize=10, fontweight='bold')

    for i, bar in enumerate(bars2):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'w/o\n{categories[i][:4]}.', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # 自动调整布局
    plt.tight_layout()

    # 显示图形
    plt.savefig('../ablation_results/single_score.pdf', dpi=500, bbox_inches='tight')
    plt.close()

def draw_ave_figures(data_dict):
    categories = list(data_dict.keys())
    values = [float(data_dict[category]['average_score'].split("±")[0]) for category in categories]
    sem = [float(data_dict[category]['average_score'].split("±")[1]) for category in categories]
    # 把all换到第一个，values和sem也要调整
    
    all_index = categories.index('All')
    categories.insert(0, categories.pop(all_index))
    values.insert(0, values.pop(all_index))
    sem.insert(0, sem.pop(all_index))
    def shorten_labels(labels):
        new_labels = []
        for label in labels:
            parts = label.split(' ')
            if len(parts) == 2 and len(parts[1]) > 4:
                # 大写第一个字母
                parts[1] = (parts[1][:4] + '.' ).capitalize()
                
            new_labels.append('\n'.join(parts))
        return new_labels

    # 使用函数处理标签
    shortened_categories = shorten_labels(categories)

    # 绘图
    fig, ax = plt.subplots()

    # 绘制较苗条的柱子，并添加误差线
    bars = ax.bar(shortened_categories, values, color='lightgrey', edgecolor='darkgrey', linewidth=1.5, width=0.4, capsize=5, alpha=0.8)

    # 添加最高值虚线
    max_value = max(values)
    ax.axhline(y=max_value, color='grey', linestyle='--')

    # 设置y轴范围
    ax.set_ylim(72, 82)

    # 隐藏x轴和y轴的轴线，但保留标签
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_alpha(0.3)

    # 删除x, y轴刻度线
    ax.tick_params(axis='x', length=0)
    ax.tick_params(axis='y', length=0)
    # 把x轴上的刻度字体变大，变粗
    for label in ax.get_xticklabels():
        label.set_fontsize(20)
        label.set_fontweight('bold')
    # 把y轴上的刻度字体变大，变粗
    for label in ax.get_yticklabels():
        label.set_fontsize(20)
        label.set_fontweight
    # 自动调整x轴标签以适应
    plt.xticks(rotation=0, ha='center')
    ax.set_ylabel('Average Score', fontdict={'fontsize': 20, 'fontweight': 'bold'})
    # ax.set_xlabel('Categories', fontdict={'fontsize': 12, 'fontweight': 'bold'})

    plt.savefig('../ablation_results/ave_score.pdf', dpi=500, bbox_inches='tight')
    plt.close()

def main():
    file_path = '../ablation_results/Metrics_ablation_all_result.xlsx'
    scores = read_score_results(file_path)
    draw_ave_figures(scores)
    draw_single_figures(scores)
    draw_radar_figures(scores)
    
# python -m AblationExp.draw_figures
if __name__ == '__main__':
    main()