import re
import logging
import requests

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page

from typing import Any, Dict, Literal

from jinja2 import Template
from git import Repo

TEMPLATE = """

---

<style>
#footer-wrapper {{
    white-space: nowrap;
}}
#footer-wrapper > p {{
    display: flex;
    align-items: center;
    gap: 5px;
    margin-top: -10px;
}}
#footer-wrapper > p > .twemoji > svg {{
    max-width: none;
}}
.contributors {{
    min-width: 30px;
    line-height: 0;
    white-space: normal;
    width: 100%;
}}
.contributors > a {{
    margin-right: -8px;
}}
.contributors > a > img {{
    width: 30px;
    border-radius: 15px;
}}
</style>

<div markdown="1" id="footer-wrapper">

:material-clock-edit-outline: {last_updated}&emsp;&emsp;:simple-github: Contributors {contributors}

</div>
"""

CONTRIBUTORS_TEMPLATE = """
<span class="contributors">
    {% for contributor in contributors %}
        <a href="{{ contributor.url }}" title="{{ contributor.id }}" target="_blank">
            <img src="{{ contributor.avatar }}" alt="{{ contributor.id }}">
        </a>
    {% endfor %}
</span>
"""

logger = logging.getLogger("mkdocs.mkdocs_turing_plugins.contributors")

class ContributorsPlugin(BasePlugin):
    config_scheme = (
        ("enabled", config_options.Type(bool, default=True)),
        ('disable_serve', config_options.Type(bool, default=True)),
    )

    enabled = True
    serve = False

    def on_startup(self, *, command: Literal['build', 'gh-deploy', 'serve'], dirty: bool) -> None:
        if command == "serve":
            self.serve = True
    
    def on_config(self, config: config_options.Config, **kwargs) -> Dict[str, Any]:
        if not self.enabled:
            return config
        
        if not self.config.get("enabled"):
            return config
        
        if self.config.get('disable_serve') and self.serve:
            self.enabled = False
            return config

        self.repo = Repo(".")

    def on_page_markdown(
        self, markdown: str, page: Page, config: config_options.Config, files, **kwargs
    ) -> str:
        if not self.enabled:
            return markdown
        
        if not self.config.get("enabled"):
            return markdown
        
        if page.meta.get("home"):
            return markdown

        src_path = "docs/" + page.file.src_path
        last_updated = self._get_last_updated(src_path)
        contributors = self._get_contributors(src_path)

        markdown = markdown + TEMPLATE.format(
            last_updated=last_updated,
            contributors=contributors
        )

        return markdown
    
    def _get_last_updated(self, path: str) -> str:
        if "general" in path and not path.endswith("index.md"):
            path = "docs/general/data.csv"
        for commit in self.repo.iter_commits(paths=path):
            return commit.committed_datetime.strftime("%Y-%m-%d")
        return "1970-01-01"

    def _get_contributors(self, path: str) -> str:
        contributors = self._fetch_contributors_from_github(path)
        if "general" in path and not path.endswith("index.md"):
            contributors.extend(
                self._fetch_contributors_from_github("docs/general/data.csv")
            )
            contributors = self._distinct(contributors)
        raw = Template(CONTRIBUTORS_TEMPLATE).render(contributors=contributors)
        return re.sub(r"(\n| {2,})", "", raw).strip()

    def _fetch_contributors_from_github(self, path: str) -> list:
        fetch_url = f"https://github.com/ZJU-Turing/TuringCourses/contributors-list/master/{path}"
        contributors = []
        try:
            res = requests.get(fetch_url)
            res.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.warning(f"Failed to fetch contributors list from {fetch_url}: {err}")
        except Exception as err:
            logger.warning(f"Exception occurred when fetching {fetch_url}: {err}")
        else:
            content = res.text
            re_results = re.findall(
                r"<a.*?href=\"/(?P<id>.*?)\".*?src=\"(?P<avatar>.*?)\"",
                content,
                re.DOTALL
            )
            for result in re_results:
                contributors.append({
                    "id": result[0],
                    "avatar": result[1].split("?")[0],
                    "url": f"https://github.com/{result[0]}"
                })
        return contributors

    @staticmethod
    def _distinct(contributors: list) -> list:
        ret = []
        for contributor in contributors:
            if contributor["id"] not in map(lambda x: x["id"], ret):
                ret.append(contributor)
        return ret