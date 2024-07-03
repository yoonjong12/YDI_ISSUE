import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

from PIL import Image, ImageTk

import time
import sys
from os.path import join, isfile
import threading

from scraper import scrap
from writer import write
from visualizer import draw
from layout import CheckboxTreeview
from llm import LLM

import pandas as pd

sys.path.append('../util')
from config import Config

config = Config('../config/config.yml').parse()
root = tk.Tk()
root.title(config['SCRAPER_TITLE'])

processing_done = False
PATH_EXCEL = config['PATH_EXCEL']
PATH_RESULT = config['PATH_RESULT']
PATH_IMG = config['PATH_IMG']
date = {'start': '', 'end': ''}

def browse(output):
    directory = filedialog.askdirectory()
    output.config(text=directory)

def browse_file(output):
    path = filedialog.askopenfilename()
    output.config(text=path)

def clear_frame(frame):
   for widgets in frame.winfo_children():
      widgets.destroy()

def open_img(path):
    return ImageTk.PhotoImage(Image.open(path).resize((800, 600)))
    
# 로딩창: 썸트렌드 수집 & 엑셀 작성
def process(args):
    args = scrap(args)  # 저장된 엑셀 파일명 반환
    excel_path = write(args)
    global processing_done
    processing_done = True

    return excel_path

def window_viz():
    def go_back():
        window.destroy()
        root.deiconify()
        
    def viz(args):
        df, path_img = draw(args)
        img = open_img(path_img+'.png')
        l_img.configure(image=img)
        l_img.image = img

        listup(df)

    def listup(df):
        keywords = list(df.index)

        for k in keywords:
            listbox.insert(tk.END, k)
        listbox.bind('<<ListboxSelect>>', on_select)

    def on_select(event):
        if listbox.curselection():
            index = listbox.curselection()[0]
            keyword = listbox.get(index)
            show_news(keyword)

    def show_news(keyword):
        def show_checked():
            indices = tree.get_checked_indices()
            articles = contents.iloc[indices]['내용'].values

            llm = LLM(keyword)
            summary = llm.analysis(articles)

            widget_summary.delete('1.0', tk.END)
            widget_summary.insert(1.0, summary)

        start, end = date['start'], date['end']
        df = pd.read_csv(join(PATH_EXCEL, keyword+'_'+start+'_'+end+'.csv'), encoding='utf-8')
        df = df.rename({'title': '제목', 'press': '언론사', 'n_reply': '댓글수', 'content': '내용'}, axis=1)
        contents = df.copy()
        df = df.drop('내용', axis=1)

        top = tk.Toplevel()
        top.geometry(config['NEWS_GEO'])
        top.title(f"뉴스 살펴보기: {keyword}")

        list_frame = ttk.LabelFrame(top, text='요약할 뉴스를 선택하세요')
        list_frame.pack(fill=tk.BOTH, expand=True)

        tree = CheckboxTreeview(list_frame, df, contents)
        tree.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=hsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="nsew")
        hsb.grid(row=1, column=0, sticky="nsew")

        button = tk.Button(list_frame, text="요약 시작", command=show_checked)
        button.grid(row=2, column=1, columnspan=2, sticky="e")

        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        frame_summary = ttk.Frame(top)
        frame_summary.pack(fill=tk.BOTH, expand=True)
    
        widget_summary = scrolledtext.ScrolledText(frame_summary, 
                                                wrap=tk.WORD, 
                                                # width=500, 
                                                font=("맑은 고딕", 15))
        
        summary = '여론 분석 결과가 여기에 표시됩니다. 분석에는 30초정도 소요됩니다.'
        widget_summary.insert(1.0, summary)
        widget_summary.pack(fill=tk.BOTH, expand=True)

    def get_box():
        load = l_ldir.cget("text")
        save = l_sdir.cget("text")
        return load, save
    
    def end():
        root.quit()
    
    window = tk.Toplevel(root)
    window.geometry(config['VIZ_GEO'])

    main_frame = ttk.Frame(window, padding=10, )
    main_frame.grid(row=0, column=0, sticky="nsew")

    # 경로 프레임
    frame_dir = ttk.LabelFrame(main_frame, padding=10, text='앞서 작성한 엑셀 파일을 불러와서 시각화 도표를 그립니다.')
    frame_dir.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    b_ldir = ttk.Button(frame_dir, text="엑셀파일 선택", command=lambda: browse_file(l_ldir))
    b_ldir.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    l_ldir = ttk.Label(frame_dir, text="엑셀파일을 먼저 선택해주세요")
    l_ldir.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    b_sdir = ttk.Button(frame_dir, text="PNG경로 선택", command=lambda: browse(l_sdir))
    b_sdir.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
    l_sdir = ttk.Label(frame_dir, text=PATH_IMG)
    l_sdir.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    b_back = ttk.Button(frame_dir, text="뒤로", command=go_back)
    b_back.grid(row=2, column=0, padx=5, pady=5, sticky="s")

    b_start = ttk.Button(frame_dir, text="그리기 시작", command=lambda: viz(get_box()))
    b_start.grid(row=2, column=1, padx=5, pady=5, sticky="s")

    b_end = ttk.Button(frame_dir, text="프로그램 종료", command=end)
    b_end.grid(row=2, column=2, padx=5, pady=5, sticky="s")

    # 키워드 리스트업
    frame_keyword = ttk.LabelFrame(main_frame, padding=10, text='키워드를 클릭하여 뉴스 요약 확인')
    frame_keyword.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

    listbox = tk.Listbox(frame_keyword)
    scrollbar = ttk.Scrollbar(frame_keyword, orient=tk.VERTICAL, command=listbox.yview)
    listbox.configure(yscrollcommand=scrollbar.set)
    listbox.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    # 이미지
    frame_img = ttk.LabelFrame(main_frame, padding=10, text='미리보기')
    frame_img.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")
    img = open_img(join(PATH_IMG, 'white.png'))
    l_img = ttk.Label(frame_img, image=img)
    l_img.image = img
    l_img.grid(row=0, padx=5, pady=5)

def start_processing(args):
    global processing_done
    processing_done = False
    window_load()
    processing_thread = threading.Thread(target=process, args=(args, ))
    processing_thread.start()

def window_load():
    def switch():
        current_text = l_load.cget("text")
        index = strings.index(current_text)  
        next_index = (index + 1) % len(strings) 
        next_text = strings[next_index] 
        l_load.config(text=next_text)  

        if not processing_done:
            window.after(1000, switch)
        else:
            window.destroy()
            window_viz()
    
    global processing_done
    processing_done = False

    window = tk.Toplevel(root)
    window.geometry(config['LOADING_GEO'])

    l_load = ttk.Label(window, text="분석 중.", font=("Helvetica", 16))
    l_load.pack(pady=20)
    strings = ["분석 중.", "분석 중..", "분석 중...", "분석 중...."]

    # 시각화 윈도우로 이동
    window.after(1000, switch)

def window_scrap():
    def add():
        keyword1 = e_key.get()
        keyword2 = e_add.get()
        combined_text = f"{keyword1}, {keyword2}"
        box.insert(tk.END, combined_text)

    def get_box():
        start = e_start.get()
        end = e_end.get()
        items = list(box.get(0, tk.END))
        dir = l_output.cget("text")
        return dir, start, end, items
    
    def start(args):
        dir, start, end, items = args

        args = {}
        args['dir'] = dir
        args['start'] = start
        args['end'] = end
        args['headless'] = config['HEADLESS']
        args['items'] = items

        date['start'] = start
        date['end'] = end

        root.withdraw()
        start_processing(args)
    
    def clear():
        box.delete(0, tk.END)

    root.geometry(config['SCRAPER_GEO'])
    
    # Create main frame
    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(row=0, column=0, sticky="nsew")

    # 저장경로 프레임
    frame_out = ttk.LabelFrame(main_frame, padding=10)
    frame_out.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    b_dir = ttk.Button(frame_out, text="저장경로 선택", command=lambda: browse(l_output))
    b_dir.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    l_output = ttk.Label(frame_out, text=PATH_EXCEL)
    l_output.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    # 날짜 프레임
    frame_date = ttk.LabelFrame(main_frame, padding=10)
    frame_date.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
    l_start = ttk.Label(frame_date, text="시작")
    l_start.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    e_start = ttk.Entry(frame_date)
    e_start.insert(0, "2024-06-20")
    e_start.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    l_end = ttk.Label(frame_date, text="종료")
    l_end.grid(row=0, column=3, padx=5, pady=5, sticky="e")
    e_end = ttk.Entry(frame_date)
    e_end.insert(0, "2024-06-25")
    e_end.grid(row=0, column=4, padx=5, pady=5, sticky="w")

    # 검색어 프레임
    frame_inp = ttk.LabelFrame(main_frame, padding=10)
    frame_inp.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

    l_key = ttk.Label(frame_inp, text="검색어")
    l_key.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    e_key = ttk.Entry(frame_inp)
    e_key.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    l_add = ttk.Label(frame_inp, text="포함어")
    l_add.grid(row=0, column=3, padx=5, pady=5, sticky="e")
    e_add = ttk.Entry(frame_inp)
    e_add.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

    b_key = ttk.Button(frame_inp, command=add, text='추가')
    b_key.grid(row=0, column=5, padx=5, pady=5, sticky="e")

    # 리스트 프레임
    frame_lst = ttk.LabelFrame(main_frame, padding=10)
    frame_lst.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")

    scroll = tk.Scrollbar(frame_lst)
    scroll.grid(row=0, column=1, rowspan=10, padx=5, pady=5, sticky="nsew")
    box = tk.Listbox(frame_lst, width=55, yscrollcommand = scroll.set)
    box.grid(row=0, column=0, rowspan=10, pady=5, sticky="nsew")    

    b_clear = ttk.Button(frame_lst, text="초기화", command=clear)
    b_clear.grid(row=8, column=2, columnspan=1, padx=5, pady=5, sticky="s")
    b_start = ttk.Button(frame_lst, text="분석 시작", command=lambda: start(get_box()))
    b_start.grid(row=9, column=2, columnspan=1, padx=5, pady=5, sticky="s")

    # Configure grid weights
    root.columnconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)

    frame_date.columnconfigure(1, weight=1)
    frame_inp.columnconfigure(2, weight=1)
    frame_lst.columnconfigure(3, weight=2)


def main():
    window_scrap()

if __name__ == "__main__":
    main()
    root.mainloop()
