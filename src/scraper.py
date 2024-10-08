import re
import os
import time
from os.path import join, isfile
from collections import defaultdict

import pandas as pd
from io import StringIO

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

from src import util
from src.config import Config

def scrap(args):
    if not args['items']:
        args = testcase(args)
    
    start = args['start']
    end = args['end']
    headless = args['headless']

    driver = init_scraper(start, end, headless)
    fnames = []
    for item in args['items']:
        item = item.split(',', 1)
        if len(item) > 1:
            keyword, subword = item
        else:
            keyword, subword = item[0], ''
        keyword, subword = keyword.strip(), subword.strip()
        args['keyword'] = keyword
        args['subword'] = subword
        driver, excel_path = search(keyword, subword, start, end, driver)
        fnames.append(excel_path)
    args['excel_ls'] = fnames
    driver.quit()
    return args

def testcase(args):
    args['start'] = '2024-06-20'
    args['end'] = '2024-06-25'
    args['headless'] = False
    args['items'] = [
        '김건희, 특검',
        '한동훈, ', 
        '노란봉투법, ' 
    ]
    return args

'''
Scraper Settings
'''
def init_scraper(start='2024-06-01', end='2024-06-04', headless=True):
    config = Config().parse()
    options = Options()
    if headless:
        options.add_argument('headless')
    else:
        options.add_experimental_option("detach", True)

    params = {
        'behavior': 'allow', 
        'download.prompt_for_download': False, 
        'download.directory_upgrade': True, 
        }
    options.add_experimental_option("prefs", params)
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), 
    #                           options=options)

    # 로그인
    driver = login(driver, config)
    driver.implicitly_wait(15)
    time.sleep(2)

    # 탭 이동
    tab = config['TAB']
    driver.get(tab)
    driver.implicitly_wait(15)
    time.sleep(2)
    for _ in range(3):
        ActionChains(driver).send_keys(Keys.ESCAPE).perform() 
        time.sleep(1)
    
    element = 'startDate'
    cnt = 0 
    while not is_opened(driver, element):
        if cnt == 5:
            raise Exception(element)

        driver = click_bar(driver)
        driver.implicitly_wait(5)
        time.sleep(2)
        cnt += 1

    # 날짜
    set_date(driver, start, end)
    return driver

def is_opened(driver, name):
    try:
        element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.NAME, name)))
        ActionChains(driver).move_to_element(element).click().perform()
        return True
    except:
        return False

def click_bar(driver):
    bar = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, 'dashboard-search-bar')))
    ActionChains(driver).move_to_element(bar).click().perform()

    return driver
    
def login(driver, config):
    ID = config['ID']
    PW = config['PW']
    LOGIN = config['LOGIN']

    driver.get(LOGIN)
    for _ in range(100):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.implicitly_wait(20)
    user_id_selector = driver.find_element(By.NAME, 'email')
    user_password_selector = driver.find_element(By.NAME, 'password')

    user_id_selector.send_keys(ID)
    user_password_selector.send_keys(PW)

    user_password_selector.send_keys(Keys.ENTER)

    return driver

def set_date(driver, start, end):
    # Start
    start_inp = driver.find_element(By.NAME, 'startDate')
    start_inp.click()
    for i in range(10):
        start_inp.send_keys(Keys.RIGHT)
    for i in range(10):
        start_inp.send_keys(Keys.BACK_SPACE)
    start_inp.send_keys(start)
    driver.implicitly_wait(1.0)

    # End
    end_inp = driver.find_element(By.NAME, 'endDate')
    end_inp.click()
    for i in range(10):
        end_inp.send_keys(Keys.RIGHT)

    for i in range(10):
        end_inp.send_keys(Keys.BACK_SPACE)

    end_inp.send_keys(end)
    driver.implicitly_wait(1.0)
    
'''
Execute
'''
def get_by_xpath(xpath, driver):
    wait = WebDriverWait(driver, 2)
    wait.until(EC.visibility_of_element_located( 
            (By.XPATH, xpath)
        ))
    elements = driver.find_elements(By.XPATH, xpath)   
    return elements 

def get_by_name(name, wait):
    element = wait.until(EC.visibility_of_element_located( 
            (By.NAME, name)
        ))
    return element
    
def get_news(driver, keyword, start, end):
    PATH_NEWS = join(util.make_path(), 'data', 'news')

    time.sleep(1)
    news_tab = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, 'id_1686800581735')))
    buttons = WebDriverWait(news_tab, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "button"))
    )
    
    news_bttn = next((button for button in buttons if button.text.lower()[:2] == '뉴스'), None)
    news_bttn.send_keys(Keys.ENTER)

    table = news_tab.find_element(By.TAG_NAME, 'table')            
    content = get_cur_news(table)
    fname = keyword + '_' + start + '_' + end + '.csv'
    fpath = join(util.make_path(), PATH_NEWS, fname)
    content.to_csv(fpath, encoding='utf-8', index=False)
    cnt = 0 
    while not isfile(fpath):
        if cnt == 5:
            raise Exception('뉴스 파일 저장 오류:', fname)
        time.sleep(3)
        cnt += 1

    return

def get_cur_news(table):
    html = table.get_attribute('outerHTML')
    table = pd.read_html(StringIO(str(html)))[0][0]
    df = defaultdict(list)
    for x in table:
        title, press, repl, cont = parse_content(x)

        df['title'].append(title)
        df['press'].append(press)
        df['n_reply'].append(repl)
        df['content'].append(cont)
    df = pd.DataFrame(df)
    return df

def parse_content(x):
    pattern1 = re.compile(r'(.+) • (댓글수 [\w,]+).+더보기(.+)')
    pattern2 = re.compile(r'(.+) • (댓글수 [\w,]+).+원문 댓글 분석(.+)')
    try:
        group = pattern1.findall(x)[0]
    except:
        group = pattern2.findall(x)[0]

    title, press = group[0].rsplit(' ', 1)
    repl = int(group[1].split()[1].replace(',', ''))
    
    return title, press, repl, group[2]


def search(keyword, subword, start, end, driver):
    PATH_SAVE = util.get_download_folder()

    excel = keyword + '_언급량 추이.xlsx'
    excel_path = join(PATH_SAVE, excel)
    csv = keyword + '_언급량 추이.csv'
    csv_path = join(PATH_SAVE, csv)
    if isfile(excel_path):
        os.remove(excel_path)
    if isfile(csv_path):
        os.remove(csv_path)
    
    wait = WebDriverWait(driver, 2)
    try:
        click_bar(driver)
    except:
        pass

    search = get_by_name('keyword', wait)
    sub_search = get_by_name('include', wait)

    # input keyword
    search.click()
    for i in range(10):
        search.send_keys(Keys.RIGHT)
    for i in range(10):
        search.send_keys(Keys.BACK_SPACE)
    search.send_keys(keyword)

    # input subword
    sub_search.click()
    for i in range(10):
        sub_search.send_keys(Keys.RIGHT)
    for i in range(10):
        sub_search.send_keys(Keys.BACK_SPACE)
    sub_search.send_keys(subword)

    # 분석하기 버튼
    buttons = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "button"))
    )
    start_button = next((button for button in buttons if button.text.lower() == '분석하기'), None)
    start_button.send_keys(Keys.ENTER)
    driver.implicitly_wait(10)
    time.sleep(1)

    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
    driver.implicitly_wait(10)
    time.sleep(3)

    # 추이 다운로드
    download = get_by_xpath('//*[@id="btn-exel-download"]', driver)[0]
    download.send_keys(Keys.ENTER)

    cnt = 0 
    while not isfile(excel_path):
        if cnt == 5:
            raise Exception('언급량 추이 다운로드 오류:', excel)
        time.sleep(3)
        cnt += 1
   
    get_news(driver, keyword, start, end)

    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
    time.sleep(1)

    return driver, excel

if __name__ == "__main__":
    scrap()