import os
from typing import Dict, Any
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page
from .utils.git_utils import get_latest_commit_timestamp

CSS_INJECTION = """
<style>
.md-content .admonition:first-of-type {
    display: none;
    margin-top: 0;
}
</style>
""".strip()

JS_INJECTION = """
<script>
(() => {
    let banner = document.querySelector(".md-content .admonition:first-of-type");
    let child = banner.children[0];
    let time_updated = new Date(child.innerText * 1000);
    let time_current = new Date();
    let diff_month = (time_current - time_updated) / 1000 / 60 / 60 / 24 / 30;
    if (diff_month > %f) {
        banner.style.display = "flow-root";
        child.innerHTML = "本页面最后更新于 " + Math.round(diff_month) + " 个月前，内容可能已经过时，请注意鉴别";
    }
})();
</script>
""".strip()

def remove_prefix(text, prefix):
    # for older versions of Python
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

class OutdateWarningPlugin(BasePlugin):
    config_scheme = (
        ("enabled", config_options.Type(bool, default=True)),
        ("month", config_options.Type(int, default=12)),
        ("exclude", config_options.Type(list, default=[])),
        ("exclude_todo", config_options.Type(bool, default=True)),
    )

    enabled = True
    exclude_list = []

    def on_config(self, config: config_options.Config, **kwargs) -> Dict[str, Any]:
        if not self.enabled:
            return config
        
        if not self.config.get("enabled"):
            return config
        
        for root, dirs, files in os.walk("./"):
            # iterate through each folder
            # for each folder, check if it has a subfolder
            # if it does, exclude its index.md
            if "index.md" in files:
                if len(dirs) > 0:
                    self.exclude_list.append(remove_prefix(os.path.join(root, "index.md"), "./docs/"))
            if root == "./docs":
                for file in files:
                    if file.endswith(".md"):
                        self.exclude_list.append(file)
        
        return config

    def on_page_markdown(
        self, markdown: str, page: Page, config: config_options.Config, files, **kwargs
    ) -> str:
        if not self.enabled:
            return markdown
        
        if not self.config.get("enabled"):
            return markdown
        
        if page.meta.get("ignore_outdate"):
            return markdown

        for file in self.exclude_list + self.config.get("exclude"):
            if page.file.src_uri == file:
                return markdown
        
        if self.config.get("exclude_todo"):
            if "#TODO" in markdown:
                return markdown
            
        file_path = page.file.abs_src_path
        if "general" in page.file.src_uri:
            if page.file.src_uri.endswith("index.md"):
                return markdown
            file_path = "docs/general/data.csv"
        page_timestamp = get_latest_commit_timestamp(file_path)
        diff_month = int(self.config.get("month"))

        markdown = "!!! warning \"%s\"\n\n\n%s\n%s%s" % (page_timestamp, markdown, CSS_INJECTION, JS_INJECTION % diff_month)

        return markdown