from chromeless import Chromeless
from example import example, second_method, assert_response, demo_url, supposed_title
import os
from PIL import Image
import sys
import pyocr
import pyocr.builders


def test_example_locally():
    chrome = Chromeless()
    chrome.attach(example)
    chrome.attach(second_method)
    title, png, divcnt = chrome.example(demo_url)
    assert_response(title, png, divcnt)


def test_example_locally_named_arg():
    chrome = Chromeless()
    chrome.attach(example)
    chrome.attach(second_method)
    title, png, divcnt = chrome.example(url=demo_url)
    assert_response(title, png, divcnt)


def test_non_toplevel_func():
    def child_func(self, url):
        self.get(url)
        return self.title
    chrome = Chromeless()
    chrome.attach(child_func)
    assert supposed_title in chrome.child_func(demo_url).lower()


def test_reserved_method_name_attached():
    def func(self, url):
        self.get(url)
        return self.title
    chrome = Chromeless()
    chrome.attach(func)
    try:
        chrome.func(demo_url).lower()
    except Exception:
        import traceback
        detail = traceback.format_exc()
        REQUIRED_SERVER_VERSION = chrome.REQUIRED_SERVER_VERSION if hasattr(
            chrome, "REQUIRED_SERVER_VERSION") else None
        if REQUIRED_SERVER_VERSION == 1 or REQUIRED_SERVER_VERSION is None:
            assert "return pickle.loads(zlib.decompress(base64.b64decode(obj.encode())))" in detail
        else:
            assert "CHROMELESS TRACEBACK IN LAMBDA START" in detail
            assert "'func' might be reserved variable name in chromeless. Please retry after re-naming." in detail
            assert "CHROMELESS TRACEBACK IN LAMBDA END" in detail


def test_error():
    chrome = Chromeless()
    from example import test_error
    test_error(chrome)


def test_language():
    chrome = Chromeless()

    def wrapper(self):
        self.get("http://example.selenium.jp/reserveApp/")
        return self.get_screenshot_as_png()

    chrome.attach(wrapper)
    png = chrome.wrapper()
    with open('./jpn.png', 'wb') as f:
        f.write(png)

    tool = pyocr.get_available_tools()[0]
    txt = tool.image_to_string(
        Image.open('./jpn.png'),
        lang='jpn',
        builder=pyocr.builders.TextBuilder()
    )
    assert "予約フォーム" in txt or "朝食バイキング" in txt
