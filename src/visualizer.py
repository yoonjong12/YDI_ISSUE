import sys
from os.path import join
from glob import glob

import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text

plt.rc('font', family='AppleGothic') # For MacOS
# plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

sys.path.append('../util')
from config import Config
config = Config('../config/config.yml').parse()

PATH_LOAD = config['PATH_RESULT']
PATH_SAVE = config['PATH_IMG']

def testcase():
    load = join(PATH_LOAD, '이슈분석_24-06-07_13-29-25.xlsx')
    save = PATH_SAVE
    return load, save

def draw(args=None):
    if args is None:
        load, save = testcase()
    else:
        load, save = args
    df = pd.read_excel(load, index_col=0)

    x, y = df['증가율'].values, df['검색수'].values
    xlabel, ylabel = '검색 증가율', '검색 수'

    x_start = x.mean()
    y_start = y.mean()
    x_left, x_right = min(x)*0.9, max(x)*0.9
    y_top, y_bottom = max(y)*0.9, min(y)*0.9

    width, height = 12*1.5, 12

    fig, ax = plt.subplots(figsize =(width, height))

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

    # ax.text(x_left, y_top, '성장', fontsize=25, ha='left', va='top', weight="bold", alpha=.5)
    # ax.text(x_right, y_top, '성숙', fontsize=25, ha='right', va='top', weight="bold", alpha=.5)
    # ax.text(x_left, y_bottom, '신생', fontsize=25, ha='left', va='bottom', weight="bold", alpha=.5)
    # ax.text(x_right, y_bottom, '쇠퇴', fontsize=25, ha='right', va='bottom', weight="bold", alpha=.5)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    path_fig = join(save, load.split('.')[0].split('/')[-1]) 
    plt.savefig(path_fig)

    # plt.show()   
    
    return df, path_fig

if __name__ == "__main__":
    draw()