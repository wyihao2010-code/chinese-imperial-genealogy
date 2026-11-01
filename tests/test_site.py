from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_tag = None
        self.in_site_nav = False
        self.current_link = None
        self.nav_links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.current_tag = tag
        if tag == "nav" and attributes.get("aria-label") == "站点导航":
            self.in_site_nav = True
        if tag == "a" and self.in_site_nav:
            self.current_link = {
                "href": attributes.get("href"),
                "classes": set(attributes.get("class", "").split()),
                "text": "",
            }

    def handle_endtag(self, tag):
        if tag == "a" and self.current_link is not None:
            self.current_link["text"] = self.current_link["text"].strip()
            self.nav_links.append(self.current_link)
            self.current_link = None
        if tag == "nav" and self.in_site_nav:
            self.in_site_nav = False
        self.current_tag = None

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        if self.current_link is not None:
            self.current_link["text"] += text


def parse_page(filename):
    parser = PageParser()
    parser.feed((ROOT / filename).read_text(encoding="utf-8"))
    return parser


class SiteNavigationTest(unittest.TestCase):
    def test_portal_links_back_to_portfolio(self):
        self.assertIn('href="https://wyihao2010-code.github.io/portfolio/"', (ROOT / "index.html").read_text(encoding="utf-8"))

    def assert_navigation(self, filename, expected_links):
        page = parse_page(filename)
        actual_links = {
            link["href"]: link["text"] for link in page.nav_links
            if "nav-link" in link["classes"]
        }
        self.assertEqual(expected_links, actual_links)
        for href in actual_links:
            if href.startswith("https://"):
                continue
            self.assertTrue(
                (ROOT / href.removeprefix("./")).is_file(),
                f"{filename} 指向不存在的页面：{href}",
            )

    def test_ming_has_home_and_qing_navigation(self):
        self.assert_navigation(
            "ming.html",
            {"./index.html": "返回首页", "./qing.html": "切换至大清", "https://wyihao2010-code.github.io/portfolio/": "返回作品集"},
        )

    def test_qing_has_home_and_ming_navigation(self):
        self.assert_navigation(
            "qing.html",
            {"./index.html": "返回首页", "./ming.html": "切换至大明", "https://wyihao2010-code.github.io/portfolio/": "返回作品集"},
        )


if __name__ == "__main__":
    unittest.main()
