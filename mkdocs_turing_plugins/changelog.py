import re, os

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page
from mkdocs.utils.meta import get_data

from typing import Any, Dict

from git import Repo

from .utils.markdown_utils import get_title

class ChangelogPlugin(BasePlugin):
    config_scheme = (
        ("enabled", config_options.Type(bool, default=True)),
    )

    enabled = True

    abbrs = {
        "嵌入式系统": ["嵌入式"],
        "计算机体系结构": ["体系结构"],
        "操作系统原理与实践": ["OS"],
        "数学分析（甲）Ⅱ（H）": ["数分Ⅱ", "数分"],
        "数学分析（甲）Ⅰ（H）": ["数分Ⅰ", "数分", "数学分析（甲）I（H）"],
        "算法竞赛集训（ACM）": ["ACM 短学期"],
        "高级数据结构与算法分析": ["ads", "ADS"],
        "数据结构基础": ["fds"],
        "面向对象程序设计": ["oop", "OOP"],
        "离散数学理论基础": ["离散"],
        "线性代数 Ⅱ（H）": ["线性代数 II（H）", "线代Ⅱ", "线代"],
        "常微分方程": ["ODE"],
        "普通物理学 Ⅱ（H）": ["普通物理学Ⅱ（H）", "普物 Ⅱ"],
        "普通物理学 Ⅰ（H）": ["普通物理学Ⅰ（H）", "普物 Ⅰ"],
        "优化基本理论与方法": ["凸优化"],
        "超算实训（HPC）": ["超算"],
        "计算机组成与设计": ["计组"],
        "理论计算机科学导引": ["计算理论", "toc", "TOC"],
        "安全攻防实践（CTF）": ["AAA 短学期"],
        "计算机系统 Ⅲ": ["计算机系统 III"],
        "人工智能基础/引论": ["人工智能基础"],
        "编译原理": ["compiler"],
        "机器学习": ["ML"],
        "数据安全与隐私保护": ["数据安全"],
        "软件安全原理和实践": ["软件安全"],
        "毛泽东思想与中国特色社会主义理论体系概论（H）": ["毛概"],
        "习近平新时代中国特色社会主义思想概论": ["习概"],
    }
    
    def on_config(self, config: config_options.Config, **kwargs) -> Dict[str, Any]:
        if not self.enabled:
            return config
        
        if not self.config.get("enabled"):
            return config

        self.repo = Repo(".")

    def on_page_markdown(
        self, markdown: str, page: Page, config: config_options.Config, files, **kwargs
    ) -> str:
        if not self.enabled:
            return markdown
        
        if not self.config.get("enabled"):
            return markdown

        if not page.meta.get("changelog"):
            return markdown
        
        changelogs = self._get_changelog_items(page)

        markdown = markdown.replace("{{ changelog }}", changelogs)

        return markdown
    
    def _get_changelog_items(self, page: Page):
        template = """- <span style="font-family: var(--md-code-font-family)">{time} [{commit_sha}]({commit_url}) </span>{commit_message}{links}"""
        res = ""
        year = 1970
        for commit in self.repo.iter_commits():
            now_year = commit.committed_datetime.year
            if now_year != year:
                year = now_year
                res += f"\n## {year} 年\n"
            commit_sha = commit.hexsha[:7]
            commit_url = f"https://github.com/ZJU-Turing/TuringCourses/commit/{commit.hexsha}"
            message = commit.message.split("\n")[0]
            if message.startswith("Merge pull request"):
                continue
            commit_message = re.sub(r"#(\d+)", r"[#\1](https://github.com/ZJU-Turing/TuringCourses/pull/\1)", message)
            time = commit.committed_datetime.strftime("%m-%d")

            changed_filenames = commit.stats.files.keys()
            docs_filenames = [
                filename for filename in changed_filenames 
                    if filename.startswith("docs/") and 
                       filename.endswith(".md") and 
                       filename.count("/") == 3 and
                       os.path.exists(filename)
            ]
            links = ""
            extra_count = 0
            for doc_path in docs_filenames:
                title = get_title(doc_path).strip()
                doc_url = doc_path.replace("docs/", "https://zju-turing.github.io/TuringCourses/").replace("index.md", "")
                search_strs = [title] + self.abbrs.get(title, [])
                _, meta = get_data(open(doc_path, "r", encoding="utf-8").read())
                if meta.get("abbrs"):
                    search_strs += meta.get("abbrs")
                for search_str in search_strs:
                    if search_str in commit_message:
                        commit_message = commit_message.replace(search_str, f"[{search_str}]({doc_url})")
                        break
                else:
                    if extra_count == 4:
                        links += "..."
                        extra_count += 1
                        continue
                    elif extra_count == 5:
                        continue
                    links += f"[{title}]({doc_url}) "
                    extra_count += 1

            if links:
                links = "\n    - 🔗 " + links
            
            res += template.format(commit_sha=commit_sha, commit_url=commit_url, commit_message=commit_message, links=links, time=time) + "\n"
        return res