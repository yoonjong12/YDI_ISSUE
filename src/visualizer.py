from os.path import join
import platform

import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text

from src import util

def testcase():
    PATH_LOAD = join(util.make_path(), 'data', 'result')
    PATH_SAVE = join(util.make_path(), 'data', 'img')

    load = join(util.make_path(), PATH_LOAD, '이슈분석_24-06-07_13-29-25.xlsx')
    save = PATH_SAVE
    return load, save

def draw(args=None):
    if platform.system() == 'Windows':
        plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows의 맑은 고딕
    elif platform.system() == 'Darwin':  # macOS의 경우
        plt.rcParams['font.family'] = 'AppleGothic'
    else:  # Linux 또는 다른 시스템의 경우
        plt.rcParams['font.family'] = 'Noto Sans CJK KR'
    plt.rcParams['axes.unicode_minus'] = False

    if args is None:
        load, save = testcase()
    else:
        load, save = args
    df = pd.read_excel(load, index_col=0)

    x, y = df['증가율'].values, df['검색수'].values
    xlabel, ylabel = '검색 증가율', '검색 수'

    x_start = x.mean()
    y_start = y.mean()

    width, height = 12*1.5, 12
    _, ax = plt.subplots(figsize =(width, height))

    ax.axhline(y=y_start, xmin=-10**9, xmax=10**9, color='black', linestyle='dashed')
    ax.axvline(x=x_start, ymin=-10**9, ymax=10**9, color='black', linestyle='dashed')

    ax.scatter(x, y, s=30)

    texts = [ax.text(x[i], y[i], df.index[i], ha='center', va='center', fontsize=13) for i in range(len(x))]
    adjust_text(texts)

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(1.02, 0.95, '성숙', transform=ax.transAxes, fontsize=25, verticalalignment='top', bbox=props)
    plt.text(-0.1, 0.95, '성장', transform=ax.transAxes, fontsize=25, verticalalignment='top', bbox=props)
    plt.text(-0.1, 0.03, '신생', transform=ax.transAxes, fontsize=25, verticalalignment='bottom', bbox=props)
    plt.text(1.02, 0.03, '쇠퇴', transform=ax.transAxes, fontsize=25, verticalalignment='bottom', bbox=props)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    path_fig = join(util.make_path(), save, load.split('.')[0].split('/')[-1]) 
    plt.savefig(path_fig)

    return df, path_fig

if __name__ == "__main__":
    draw()