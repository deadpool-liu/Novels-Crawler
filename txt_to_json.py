# encoding=utf-8
import os
import sys
import glob
import json
import math

# 按文件大小切分成不同大小的文件，随机性较强
def split_file(file, json_str):
    str_size = round(sys.getsizeof(str(json_str)) / float(1024 * 1024), 2)
    print(str_size)
    if str_size <= 20:
        print("章节数", len(json_str.get("chapterList")))
        new_file = json.dumps(json_str, ensure_ascii=False)
        file_ = file.replace("./101-200/101-200", "./101-200/101-200(finish)")[:-3] + "json"

        with open(file_, "w", encoding="iso-8859-1") as f:
            f.write(new_file)
        print("已经写完", file_)
    else:
        file_count = math.floor(str_size / 15)
        files = [file.replace("./101-200/101-200", "./101-200/101-200(finish)")[:-4] + "_" + str(i + 1) + ".json" for i
                 in range(file_count)]
        # print(files)
        chapter_count = math.floor(len(json_str.get("chapterList")) / file_count)

        for index, file_ in enumerate(files):
            # 前面部分
            if index == 0:
                new_file_ = {"name": json_str.get("name"),
                             "description": json_str.get("description"),
                             "chapterList": json_str.get("chapterList")[:chapter_count]}
                print("章节数", len(new_file_.get("chapterList")))
                new_file = json.dumps(new_file_, ensure_ascii=False)

                with open(file_, "w", encoding="iso-8859-1") as f:
                    f.write(new_file)
                print("已经写完", file_)
            # 最后部分
            elif index == len(files) - 1:
                new_file_ = {"chapterList": json_str.get("chapterList")[chapter_count * index:]}
                print("章节数", len(new_file_.get("chapterList")))
                new_file = json.dumps(new_file_, ensure_ascii=False)
                with open(file_, "w", encoding="iso-8859-1") as f:
                    f.write(new_file)
                print("已经写完", file_)
            # 中间部分
            else:
                new_file_ = {"chapterList": json_str.get("chapterList")[chapter_count * index:chapter_count * (1 + index)]}
                print("章节数", len(new_file_.get("chapterList")))
                new_file = json.dumps(new_file_, ensure_ascii=False)
                with open(file_, "w", encoding="iso-8859-1") as f:
                    f.write(new_file)
                print("已经写完", file_)


def txt_to_json(file):
    f = list(open(file, "r", encoding="iso-8859-1"))
    # # 去除空行
    # while "\n" in f:
    #     f.remove("\n")
    new_file = {"name": f[0].strip(),
                # "image": f[1].strip(),
                "description": f[2].strip(),
                "chapterList": []}
    this_chapter = {"title": f[3].strip(),
                    "content": "none"}
    new_content = ""

    # 去除和章节名称相同内容的段落首行
    for index, line in enumerate(f):
        if index < len(f) - 1:
            if "\t" not in line:
                if line.strip() == f[index + 1].strip() and "\t" in f[index + 1]:
                    f[index + 1] = "\t"

    for index, line in enumerate(f[3:]):
        line = line.encode("utf-8").decode("utf-8")
        if line != "\t":
            # print(line)
            if "\t" not in line:

                if index > 1:
                    this_chapter["content"] = new_content
                    new_file["chapterList"].append(this_chapter)
                    this_chapter = {"title": line,
                                    "content": "none"}
                    new_content = ""

            else:
                new_content += line

            if index == len(f[3:]) - 1:
                this_chapter["content"] = new_content
                new_file["chapterList"].append(this_chapter)

    fi = file.replace("./novels301-445", "./NovelsJson").replace("txt", "json")
    print(fi)
    with open(fi, "w", encoding="iso-8859-1") as f:
        f.write(json.dumps(new_file, ensure_ascii=False))

    # split_file(file, json_str=new_file)


if __name__ == '__main__':
    files = glob.glob("./novels301-445/*.txt")
    for file in files:
        print(file)
        # print(file.replace("./novels\\", "./NovelsJson/").replace("txt", "json"))
        txt_to_json(file)
        # get_file_size(file)
        print("=" * 100)
    # print("ï»¿")
    # 判断文件大小
    # json_str = {
    #     "test": "effect",
    #     "ttt": 990
    # }
    # size = round(sys.getsizeof(str(json_str)) / float(1024 * 1024), 2)
    # print(size)
