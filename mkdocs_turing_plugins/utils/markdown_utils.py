import re

def get_title_from_content(markdown: str) -> str:
    return re.search(r"^# (.*)", markdown, re.M).group(1)

def get_title(path: str) -> str:
    return get_title_from_content(open(path, "r", encoding="utf-8").read())