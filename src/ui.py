from os.path import join
import threading

import pandas as pd
import tkinter as tk
from tkinter import ttk, scrolledtext

from src import util
from src.config import Config
from src.scraper import scrap
from src.writer import write
from src.visualizer import draw
from src.layout import CheckboxTreeview
from src.llm import LLM

# 1. 크롤링 
def window_scrap(root, config):
    date = {'start': '', 'end': ''}
    KEY = util.load_key()
    HEADLESS = True

    def add():
        keyword1 = e_key.get()
        keyword2 = e_add.get()
        combined_text = f"{keyword1}, {keyword2}"
        box.insert(tk.END, combined_text)

    def get_box():
        start = e_start.get()
        end = e_end.get()
        items = list(box.get(0, tk.END))
        return start, end, items
    
    def start(args):
        start, end, items = args
        config['start'] = start
        config['end'] = end
        config['root'] = root
        config['headless'] = HEADLESS
        config['items'] = items

        root.withdraw()
        start_processing(config)
    
    def clear():
        box.delete(0, tk.END)

    def delete_selected():
        selected_indices = box.curselection()
        for index in reversed(selected_indices):
            box.delete(index)

    def open_key_window():
        def save_and_close():
            new_key = key_entry.get()
            util.save_key(new_key)
            label_status.config(text="OPENAI Key가 입력되어있습니다", foreground="blue")
            key_window.destroy()
        
        # 새 창 생성
        key_window = tk.Toplevel(root)
        key_window.title("키 입력")
        
        # 텍스트 입력 필드
        key_entry = ttk.Entry(key_window, width=30)
        key_entry.pack(padx=10, pady=10)
        key_entry.insert(0, KEY if KEY else "OPENAI Key를 여기에 붙여넣으세요")  # 기존 텍스트가 있으면 표시
        
        # 저장 버튼
        save_button = ttk.Button(key_window, text="저장", command=save_and_close)
        save_button.pack(padx=10, pady=10)

    def toggle_headless():
        global HEADLESS
        HEADLESS = not check_var.get()  # 체크박스가 체크되면 False, 해제되면 True

    root.geometry(config['SCRAPER_GEO'])
    
    # Create main frame
    main_frame = ttk.Frame(root, padding=10)
    main_frame.grid(row=0, column=0, sticky="nsew")

    # 초기 설정 프레임
    frame_setting = ttk.LabelFrame(main_frame, padding=10)
    frame_setting.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    frame_setting.grid_columnconfigure(2, weight=1)  # 2번째 열(체크박스 열)을 확장
    
    b_key = ttk.Button(frame_setting, text="OPENAI Key 입력", command=open_key_window)
    b_key.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    if KEY:
        label_status = ttk.Label(frame_setting, text="OPENAI Key가 입력되어있습니다", foreground="blue")
    else:
        label_status = ttk.Label(frame_setting, text="OPENAI Key가 아직 입력되어있지 않습니다", foreground="red")
    label_status.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    check_var = tk.BooleanVar(value=False)
    checkbox = ttk.Checkbutton(
        frame_setting, 
        text="크롤링 과정 보기", 
        variable=check_var, 
        command=toggle_headless
    )
    checkbox.grid(row=0, column=2, padx=5, pady=5, sticky="e")

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

    b_delete = ttk.Button(frame_lst, text="삭제", command=delete_selected)
    b_delete.grid(row=7, column=2, columnspan=1, padx=5, pady=5, sticky="s")
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

# 2. 시각화 & 뉴스 요약
def window_viz(root, config):
    PATH_NEWS = join(util.make_path(), 'data', 'news')
    PATH_RESULT = join(util.make_path(), 'data', 'result')
    PATH_IMG = join(util.make_path(), 'data', 'img')

    def go_back():
        window.destroy()
        root.deiconify()
        
    def viz(args):
        df, path_img = draw(args)
        img = util.open_img(path_img+'.png')
        l_img.configure(image=img)
        l_img.image = img

        keywords = list(df.index)
        listbox.delete(0, tk.END)
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

        start, end = config['start'], config['end']
        df = pd.read_csv(join(util.make_path(), PATH_NEWS, keyword+'_'+start+'_'+end+'.csv'), encoding='utf-8')
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
        
        summary = '여론 분석 결과가 여기에 표시됩니다. 선택한 문서 개수에 따라 30초 ~ 5분까지 소요될 수 있습니다. 과도하게 많이 선택할 시, ChatGPT 입력 초과로 오류가 발생할 수 있습니다.'
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

    b_ldir = ttk.Button(frame_dir, text="엑셀파일 선택", command=lambda: util.browse_file(l_ldir, PATH_RESULT))
    b_ldir.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    l_ldir = ttk.Label(frame_dir, text="엑셀파일을 먼저 선택해주세요")
    l_ldir.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    b_sdir = ttk.Button(frame_dir, text="PNG경로 선택", command=lambda: util.browse(l_sdir, PATH_IMG))
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
    img = util.open_img(join(PATH_IMG, 'white.png'))
    l_img = ttk.Label(frame_img, image=img)
    l_img.image = img
    l_img.grid(row=0, padx=5, pady=5)

def start_processing(args):
    global processing_done
    processing_done = False
    window_load(args['root'], args)
    processing_thread = threading.Thread(target=process, args=(args, ))
    processing_thread.start()

def window_load(root, config):
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
            window_viz(root, config)
    
    global processing_done
    processing_done = False

    window = tk.Toplevel(root)
    window.geometry(config['LOADING_GEO'])

    l_load = ttk.Label(window, text="분석 중.", font=("Helvetica", 16))
    l_load.pack(pady=20)
    strings = ["분석 중.", "분석 중..", "분석 중...", "분석 중...."]

    # 시각화 윈도우로 이동
    window.after(1000, switch)


# 로딩창: 썸트렌드 수집 & 엑셀 작성
def process(args):
    args = scrap(args)  # 저장된 엑셀 파일명 반환
    excel_path = write(args)
    global processing_done
    processing_done = True

    return excel_path

def main():
    config = Config().parse()
    root = tk.Tk()
    root.title(config['SCRAPER_TITLE'])

    window_scrap(root, config)
    root.mainloop()

if __name__ == "__main__":
    main()
