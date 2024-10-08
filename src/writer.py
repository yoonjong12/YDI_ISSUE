import os
from os.path import join
from datetime import datetime
import pandas as pd
from src import util

def get_sum(df):
    return df.sum(axis=1)

def get_diff(df):
    df = df.iloc[0].values
    a, b = df[0], df[-1]
    num = b-a  if (b-a) != 0 else 1
    a = a if a != 0 else 1
    return num / a

def write(args=None):
    PATH_LOAD = util.get_download_folder()
    PATH_SAVE = join(util.make_path(), 'data', 'result')

    if args is None:
        args = testcase()

    excels = args['excel_ls']
    fname = '이슈분석_' + datetime.today().strftime('%y-%m-%d_%H-%M-%S') + '.xlsx'

    dfs = []
    for path in excels:
        name = path.split('_', 1)[0]
        df = pd.read_excel(join(PATH_LOAD, path), sheet_name=f'{name}')
        df = df.rename({'전체': name}, axis=1)
        df = df[['날짜', name]].set_index('날짜').T

        sum_ = get_sum(df)
        diff = get_diff(df) 
        df['검색수'] = sum_
        df['증가율'] = diff * -1
        dfs.append(df)

        os.remove(join(PATH_LOAD, path))

    df = pd.concat(dfs)

    path_save = join(util.make_path(), PATH_SAVE, fname)
    df.to_excel(path_save)
    return path_save

def testcase():
    args = {}
    return args

if __name__ == "__main__":
    write()