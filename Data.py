import subprocess
import os.path
import json
import time
import urllib.parse
from typing import Any, Tuple
import config
from requests_html import HTMLSession
from markdownify import markdownify


class Data:
    def __init__(
        self,
        data_file_path: str = config.DATA_FILE_PATH,
        preload: bool = False,
        fetch_rule: bool = True,
    ) -> None:
        super().__init__()
        self.data_file_path = data_file_path
        data = None
        if preload:
            data = self.load()  # load from existing data file
            if (  # check whether the data file is valid
                not data
                or abs(time.time() - data["timestamp"]) / 60
                > config.DATA_RENEW_THRESHOLD_IN_MIN
            ):
                data = self.fetch()
        self.data = data

    def load(self, path: str = None) -> Any:
        data = None
        if not path:
            path = self.data_file_path

        if os.path.exists(path):
            with open(path, "r") as fp:
                data_ser = json.load(fp)
                data = json.loads(data_ser)

        self.data = data
        return data

    def fetch(self, url: str = config.DATA_API_URL) -> Any:
        # fetcch data
        print("\n-------------Start fetching data-------------")
        r = subprocess.check_output(f"curl {url}", shell=True)
        print("\n-------------Finish fetching data-------------")

        print("\n-------------Start serializing data-------------")
        json_data = json.loads(r.decode("utf-8"))

        # indexing based on question frontend id
        data = {}
        for q in json_data["stat_status_pairs"]:
            qid = q["stat"]["frontend_question_id"]
            if qid in data:
                raise RuntimeError(f"question #{qid} already exists, duplicate!")
            else:
                data[str(qid).zfill(config.QID_PADDING_SIZE)] = q

        print(f"Total feteched questions: {len(data)} ")
        data["timestamp"] = time.time()
        print("\n-------------Finish serializing data-------------")

        return data

    def do_persistence(
        self, data_serialized: str = None, path=config.DATA_FILE_PATH
    ) -> None:
        print("\n-------------Start data persistence-------------")
        if not data_serialized:
            data_serialized = json.dumps(self.data)

        if not data_serialized or not path:
            raise RuntimeError("invalid input data or file path.")

        with open(path, "w") as fp:
            json.dump(data_serialized, fp)
        print("\n-------------Finish data persistence-------------")


class Problem:
    def __init__(self, qid: int, blob: Any, auto_parse=False) -> None:
        super().__init__()
        self.qid = str(qid).zfill(config.QID_PADDING_SIZE)
        self.difficulty = blob["difficulty"]["level"]
        self.is_paid = blob["paid_only"]
        self.stat = blob["stat"]
        if auto_parse:
            self.parse(self.stat)

    def parse(self, stat=None):
        self.total_acs, self.total_submitted, self.ac_rate = self._parse_statistics(
            stat
        )
        self.title = self._parse_title(stat)
        self.title_slug = self._parse_title_slug(stat)
        self.url = self._parse_url(stat)
        self.url_solution = self._parse_url_solution(stat)

    def _parse_statistics(self, stat) -> Tuple[int, int]:
        acs, submissions = stat["total_acs"], stat["total_submitted"]
        return acs, submissions, acs / submissions if submissions > 0 else 0

    def _parse_title(self, stat):
        return stat["question__title"]

    def _parse_title_slug(self, stat):
        return stat["question__title_slug"]

    def _parse_url(self, stat):
        title_slug = self._parse_title_slug(stat)
        return urllib.parse.urljoin(config.PROBLEM_URL_PREFIX, title_slug)

    def _parse_url_solution(self, stat):
        # be careful about the urljoin behavior: base abs url + part only(will swap if exists)
        return (
            urllib.parse.urljoin(
                config.PROBLEM_URL_PREFIX, stat["question__article__slug"] + "/solution"
            )
            if stat["question__article__slug"]
            else None
        )

    def _scrape(self, url=None):
        if not url:
            url = self.url
        r = HTMLSession().get(url)
        r.html.render()

        # self.content, self.contetnt_md = self._scrape_problem_content(r.html)
        with open("html-content.html", "w") as f:
            f.write(r.html.html)
        with open("html-raw-content.html", "w") as f:
            f.write(r.raw_html)
        self.tags = self._scrape_problem_topics(r.html)
        self.tags = self._scrape_problem_companies(r.html)

    def _scrape_problem_topics(self, html):
        t_elements = html.xpath("//a[starts-with(@class,'topic-tag')]/span")

        return [t.text for t in t_elements]

    def _scrape_problem_companies(self, html):
        # companies tags are only available to paid user.
        # TODO: add login and cookies support
        t_elements = html.xpath("//a[starts-with(@href,'/company')]")

        return [t.text for t in t_elements]

    def _scrape_problem_content(self, html):
        content = html.xpath("//div[contains(@class,'question-content')]/div")[0]
        markdown_content = markdownify(self.html_preprocess(content.html))
        # with open("test.md", "w") as fp:
        #     fp.write(md_out)
        return content, markdown_content

    def html2markdown_preprocess(self, html: str) -> str:
        # replace all <code>,</code> to inline markdown code: `backtip`
        # replace all \n newline to <br> in html, otherwise it cannot be parsed as newline
        # replace all <pre></pre> to code block ```, default type is json for better display

        res = (
            html.replace("<code>", "`")
            .replace("</code>", "`")
            .replace("\n", "<br>")
            .replace("<pre>", "```json<br>")
            .replace("</pre>", "```<br>")
        )

        return res