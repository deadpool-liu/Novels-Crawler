import os
import sys
import time
import pandas
import traceback
import requests
from lxml import etree
import tqdm
import threading
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import multiprocessing
import selenium
from selenium import webdriver
from selenium import common
import sys

sys.setrecursionlimit(10000000)


def get_response(url):
    state = False
    request_times = 1
    while not state:
        try:
            time.sleep(0.01)
            result = requests.get(url)
            print("\r", time.strftime('%Y-%m-%d %H-%M-%S', time.localtime()), "状态码：", result.status_code, end="")
            try:
                pa = etree.HTML(result.text)
                first_url = pa.xpath('//div[@class="bookinfo-wg"]/div[@class="row"]//div[@class="actions"]/a[@class="read"]/@href')
                if first_url:
                    return result.text
                if request_times > 50:
                    return result.text
                request_times += 1

            except:
                time.sleep(10)
        except requests.exceptions.SSLError:
            print("访问过于频繁，当前URL:", url)
            time.sleep(60)
        except:
            print("意外bug:", url)
            traceback.print_exc()
            time.sleep(20)


def get_novel_url_in_eight_type():
    novel_urls = [[], []]
    type_url = ["https://swnovels.com/romance-bc8.html",
                "https://swnovels.com/urban-bc91.html",
                "https://swnovels.com/werewolf-bc36.html"]

    for one_url in type_url:
        print()
        print(one_url)
        for one_page in range(50):  # 首次 5
            url = one_url + "?page=" + str(one_page)

            res = get_response(url)
            pa = etree.HTML(res)

            novel_url_path = """//div[@class="row book-row"]//div[@class="info pull-left"]/a/@href"""
            novel_title_path = """//div[@class="row book-row"]//div[@class="info pull-left"]/a/h3/text()"""

            novel_url = pa.xpath(novel_url_path)
            novel_title = pa.xpath(novel_title_path)

            novel_url = ["https://swnovels.com" + o for o in novel_url]

            if len(novel_url) > 0:
                for u, t in zip(novel_url, novel_title):
                    novel_urls[0].append(u)
                    novel_urls[1].append(t)

    return novel_urls


def expand_shadow_element(elements, driver):
    print("shadow_roots_count", len(elements))

    shadow_roots = []
    for element in elements:
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)

        shadow_roots.append(shadow_root)

    return shadow_roots


def get_one_page(driver, url, file, title):
    state = False
    retry = False
    request_times = 1
    while not state:

        try:
            if not retry:
                driver.get(url)
            else:
                driver.get(driver.current_url)

            time.sleep(1)

            try:
                next_url = driver.find_element_by_xpath(
                    """//div[@class="col-lg-12 col-md-12"]//a[@class="btn btn-success next"]""").get_attribute("href")
                if next_url:
                    return driver



            except:
                request_times += 1
                if request_times > 10:
                    return driver
                print("没有找到下一页地址，重新加载中")
                time.sleep(10)


        except selenium.common.exceptions.TimeoutException:
            # print("url", "有问题的url", url, "=" * 200)
            # traceback.print_exc()
            time.sleep(5)
        except:
            if not os.path.exists("./logs"):
                os.mkdir("./logs")
            log_time = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
            # with open("./logs/{}.txt".format(file), "a+") as f:
            #     f.write("=" * 100 + "\n")
            traceback.print_exc(file=open("./logs/{}.txt".format(file), "a+"))
            with open("./logs/{}.txt".format(file), "a+") as f:
                f.write("\n" + "url:" + url)
                f.write("\n" + "log_time:" + log_time)
                f.write("\n" + "title:" + title)
            # with open("./logs/{}.txt".format(file), "a+") as f:
            #     f.write("=" * 100 + "\n" * 10)
            print("{:=^100}".format("非正常bug，已写入日志"), "\nurl为:", url)
            sys.stdout.flush()
            time.sleep(300)
            retry = True


def get_data_for_excel(url):
    res = get_response(url)
    pa = etree.HTML(res)

    genre_path = '//div[@class="bookinfo-wg"]//tr[@class="categories"]/td[@class="value"]//text()'
    author_path = '//div[@class="bookinfo-wg"]//tr[@class="authors"]/td[@class="value"]//text()'
    views_path = '//div[@class="bookinfo-wg"]//tr[@class="total-view"]/td[@class="value"]//text()'
    num_chapters_path = '//div[@class="bookinfo-wg"]//tr[@class="num-chapters"]/td[@class="value"]//text()'
    status_path = '//div[@class="bookinfo-wg"]//tr[@class="status"]/td[@class="value"]//text()'
    newest_chapter_path = '//div[@class="bookinfo-wg"]//tr[@class="newest-chapter"]/td[@class="value"]//text()'

    genre_ = pa.xpath(genre_path)
    author_ = pa.xpath(author_path)
    views_ = pa.xpath(views_path)
    num_chapters_ = pa.xpath(num_chapters_path)
    status_ = pa.xpath(status_path)
    newest_chapter_ = pa.xpath(newest_chapter_path)

    print()
    print(genre_)
    print(author_)
    print(views_)
    print(num_chapters_)
    print(status_)
    print(newest_chapter_)

    return genre_, author_, views_, num_chapters_, status_, newest_chapter_


def get_first_page(file, url, title):
    res = get_response(url)
    pa = etree.HTML(res)

    first_page_url_path = """//div[@class="bookinfo-wg"]/div[@class="row"]//div[@class="actions"]/a[@class="read"]/@href"""
    image_url_path = """//div[@class="container"]//div[@class="bookinfo-wg"]//div[@class="img-container"]//img/@data-src"""
    description_path = """//div[@class="chapter-info-wg"]//div[@class="tab-content"]//div[@id="bookinfo"]/text()
    |//div[@class="chapter-info-wg"]//div[@class="tab-content"]//div[@id="bookinfo"]//p//text()"""

    first_page_url = pa.xpath(first_page_url_path)
    image_url = pa.xpath(image_url_path)
    description = pa.xpath(description_path)

    first_page_url = ["https://swnovels.com" + fi for fi in first_page_url]
    desc = ""
    for d in description:
        if d.strip() != "":
            desc += d.strip()+"\t"

    print("第一章节的url为：", first_page_url)
    print("小说封面的图片", image_url)
    print("小说的description：", desc)

    if len(first_page_url) >= 1:
        with open(file, "w", encoding="utf-8-sig") as f:
            f.write(title + "\n")
            if image_url:
                f.write(image_url[0] + "\n")
            else:
                f.write("\n")
            f.write(desc + "\n")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-gpu')  # 用来规避bug
        chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不显示图片
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # chrome_options.headless = True  # 无界面模式

        chrome_options.add_argument("--window-size=300,200")
        # chrome_options.add_argument("--window-position=1600, 0")
        chrome_options.add_extension("./extension/reload.crx")
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,
                'javascript': 1,
                'stylesheet': 2  # 2即为禁用的意思
            }
        }
        chrome_options.add_experimental_option('prefs', prefs)

        driver = webdriver.Chrome("D:/my workspace（勿删，重要）/尚阡/swnovels.com/webdriver/chromedriver.exe",
                                  options=chrome_options)
        driver.set_window_rect(1600, 0, 300, 200)
        # driver.implicitly_wait(1000)
        # driver.set_page_load_timeout(3000)
        time.sleep(1)
        get_next_chapter(file, first_page_url[0], title, driver)
    else:
        print("该小说的内容为空，未爬取，已保存记录", url)
        with open("./NoneNovel/{}".format(file.strip("./novels/")), "a+", encoding="utf-8-sig") as f:
            f.write(title + "\t" + str(time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())))


def get_next_chapter(file, url, title, driver):
    driver = get_one_page(driver, url, file, title)
    try:
        chapter_title = driver.find_elements_by_xpath("""//section[@class="breadcrumb-section"]//li[
        @class="active"]//font[@style="vertical-align: inherit;"]|//section[@class="breadcrumb-section"]//li[
        @class="active"]//a""")
    except:
        chapter_title = [""]
    try:
        next_url = driver.find_element_by_xpath(
            """//div[@class="col-lg-12 col-md-12"]//a[@class="btn btn-success next"]""").get_attribute("href")
    except:
        next_url = ""
    contents_ordinary = driver.find_elements_by_xpath("""//p""")

    shadow_roots = driver.find_elements_by_xpath("""//div[@class='ctp']""")

    contents_shadow_root = expand_shadow_element(shadow_roots, driver)

    chapter_title = [ch.text.strip() for ch in chapter_title]
    content = [c.text.strip() for c in contents_ordinary]
    # print("正常内容", content)

    for one in contents_shadow_root:
        if one:
            co = one.find_elements_by_css_selector("p")
            for c in co:
                # print("c", c.text.strip())
                content.append(c.text.strip())

    while "" in chapter_title:
        chapter_title.remove("")
    while "" in content:
        content.remove("")

    with open(file, "a", encoding="utf-8-sig") as f:
        if len(chapter_title) >= 1:
            f.write(chapter_title[0] + "\n")
            print("章节title与url", chapter_title[0], url)
            sys.stdout.flush()
        else:
            f.write("Chapter" + "\n")
        for index, line in enumerate(content):
            if line != "":
                f.write("\t" + line + "\n")

    if next_url.strip():
        get_next_chapter(file, next_url, title, driver)
    else:
        print("下一页的数量为：{}，所有的url为：{}".format(len(next_url), next_url))
        driver.close()


if __name__ == '__main__':
    ####################################################################################################################
    # # 创建存储小说的文件夹novels，内容为空的小说文件
    # dirs = ["./novels", "./NoneNovel"]
    # for dir_ in dirs:
    #     if not os.path.exists(dir_):
    #         os.mkdir(dir_)
    #
    # print("正在获取所有小说的url和title")
    ####################################################################################################################
    # # 获取小说的title并保存，与小说内容分开获取，易于调试更加稳定
    # # sys.stdout.flush()
    # urls_and_titles = get_novel_url_in_eight_type()
    # urls = []
    # titles = []
    # for index, u in enumerate(urls_and_titles[0]):
    #     if u not in urls:
    #         urls.append(u)
    #         titles.append(urls_and_titles[1][index])
    #
    # # #
    # with open("./novellist.txt", "w", encoding="utf-8") as f:
    #     for i in range(len(urls)):
    #         f.write(urls[i] + "\t")
    #         f.write(titles[i] + "\n")
    ####################################################################################################################
    # 从本地保存的小说url和title中读取数据
    f = list(open("./novellist.txt", encoding="utf-8-sig"))
    urls = []
    titles = []
    for one in f:
        urls.append(one.split("\t")[0])
        titles.append(one.split("\t")[1].strip())

    novel_count = len(urls)
    print("小说数量：", novel_count)  #

    files = ["./novels/swnovels.com.{:0>6}.txt".format(i + 1) for i in range(novel_count)]
    ####################################################################################################################
    # # 用于生成Excel表格
    # genre_list = []
    # author_list = []
    # views_list = []
    # num_chapters_list = []
    # status_list = []
    # newest_chapter_list = []
    #
    # for url in tqdm.tqdm(urls):
    #     genre, author, views, num_chapters, status, newest_chapter = get_data_for_excel(url)
    #     genre_list.append(genre)
    #     author_list.append(author)
    #     views_list.append(views)
    #     num_chapters_list.append(num_chapters)
    #     status_list.append(status)
    #     newest_chapter_list.append(newest_chapter)
    # data = {"BookName": titles,
    #         "Genres": genre_list,
    #         "Authors": author_list,
    #         "Views": views_list,
    #         "Num-Chapters": num_chapters_list,
    #         "Status": status_list,
    #         "Newest-Chapters": newest_chapter_list,
    #         "Files": files,
    #         "Url": urls}
    # data = pandas.DataFrame(data)
    # data.to_excel("./swnovels.com.xlsx")
    # print("\n{:-^100}".format("excel数据已保存"))
    ###################################################################################################################
    # 线程池爬取所有小说
    # 分批次处理
    files = files[440:]
    urls = urls[440:]
    titles = titles[440:]

    print(files)
    print(urls)
    print(titles)

    t1 = time.time()
    pool = ThreadPoolExecutor(max_workers=8)
    all_task = []
    for one_novel_task in range(len(urls)):
        task = pool.submit(lambda p: get_first_page(*p), (files[one_novel_task],
                                                          urls[one_novel_task],
                                                          titles[one_novel_task]))
        all_task.append(task)
    wait(all_task, return_when=ALL_COMPLETED)
    t2 = time.time()
    print("已结束，本次运行时间:", (t2-t1)/60/60, "h")
    # ####################################################################################################################
    # 进程池爬取所有小说
    # 分批次处理
    # files = files[10:50]
    # urls = urls[10:50]
    # titles = titles[10:50]
    #
    # pool = multiprocessing.Pool(8)
    # t1 = time.time()
    # for one_novel_task in range(40):
    #     pool.apply_async(get_first_page, (files[one_novel_task],
    #                                       urls[one_novel_task],
    #                                       titles[one_novel_task]))
    # pool.close()
    # pool.join()
    #
    # t2 = time.time()
    # print("已结束，本次运行时间:", (t2-t1)/60/60, "h")
