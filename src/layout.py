import tkinter as tk
from tkinter import ttk, scrolledtext
import pandas as pd

import sys
sys.path.append('../util')
from config import Config
config = Config('../config/config.yml').parse()

class CheckboxTreeview(ttk.Treeview):
    def __init__(self, master, df, contents, **kwargs):
        columns = ["Check"] + list(df.columns) + ["Click"]
        super().__init__(master, columns=columns, show="headings", **kwargs)
        
        self.df = df
        self.contents = contents
        self.checked = set()

        self.width_dict = {
            '제목': 500, 
            '언론사': 20, 
            '댓글수': 20, 
            '내용': 50,
            'Check': 20,
            'Click': 50
        }

        # Configure columns
        self.heading("Check", text="요약 선택")
        self.column("Check", width=50, anchor="center")
        
        for col in df.columns:
            self.heading(col, text=col)
            self.column(col, width=self.width_dict[col])  # You can adjust this or make it dynamic
        
        self.heading("Click", text="클릭하여 원문 확인")
        self.column("Click", width=50, anchor="center")
        
        # Insert data
        for index, row in df.iterrows():
            values = ["☐"] + list(row) + [""]
            item = self.insert("", "end", iid=str(index), values=values)
            self.set(item, "Click", "Click")
        
        self.bind("<ButtonRelease-1>", self.on_click)
    
    def on_click(self, event):
        region = self.identify("region", event.x, event.y)
        if region == "cell":
            column = self.identify_column(event.x)
            item = self.identify_row(event.y)
            if column == "#1":  # Check column
                self.toggle_check(item)
            elif column == f"#{len(self.cget('columns'))}":  # Click column
                self.show_index(item)
    
    def toggle_check(self, item):
        current_values = self.item(item, 'values')
        if current_values[0] == "☐":
            new_values = ("☑",) + current_values[1:]
            self.checked.add(item)
        else:
            new_values = ("☐",) + current_values[1:]
            self.checked.discard(item)
        self.item(item, values=new_values)
    
    def get_checked_indices(self):
        return [int(item) for item in self.checked]

    def show_index(self, item):
        index = int(item)
        top = tk.Toplevel(self.master)
        top.title("뉴스 원문보기")
        top.geometry(config['CONTENT_GEO'])
        label = scrolledtext.ScrolledText(top, 
                                            wrap=tk.WORD, 
                                            width=500, 
                                            font=("맑은 고딕", 15))
        label.pack(pady=20)
        label.insert(1.0, self.contents.iloc[index]['내용'])

def display_dataframe(df):
    root = tk.Tk()
    root.title("DataFrame Viewer")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    tree = CheckboxTreeview(frame, df, df)
    tree.pack(fill=tk.BOTH, expand=True)

    def show_checked():
        indices = tree.get_checked_indices()
        result_label.config(text=f"Checked indices: {indices}")

    start_button = tk.Button(root, text="Start", command=show_checked)
    start_button.pack(pady=5)

    result_label = tk.Label(root, text="")
    result_label.pack(pady=5)

    root.mainloop()

# Example usage
if __name__ == "__main__":
    # Create a sample DataFrame
    data = {
        '제목': ['John', 'Alice', 'Bob', 'Charlie'],
        '언론사': [28, 24, 22, 30],
        '내용': ['New York', 'San Francisco', 'Los Angeles', 'Chicago']
    }
    df = pd.DataFrame(data)

    # Display the DataFrame
    display_dataframe(df)