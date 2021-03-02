#!/usr/bin/env python


from collections import OrderedDict
from starter import menu
from starter import utils


def test_show_heading(caplog):
    m = menu.Text_Menu("test menu", """Line 1\nLine 2\nLine 3""")
    for level in utils.Log_level.__args__:
        with caplog.at_level(menu.logger.level(level).no):
            caplog.clear()
            m.show_heading(level)
            assert caplog.messages == [f"{x}" for x in m.heading.split("\n")]


def test_show_separator(caplog):
    m = menu.Text_Menu("test menu", """Line 1\nLine 2\nLine 3""")
    for level in utils.Log_level.__args__:
        with caplog.at_level(menu.logger.level(level).no):
            caplog.clear()
            m.show_separator(level)
            assert tuple(map(len, caplog.messages)) == (1 + 42,)


def test_show_options(caplog):
    m = menu.Text_Menu("test menu", """Line 1\nLine 2\nLine 3""")
    opts = OrderedDict((
        ("A", "one option"),
        ("B", "another option"),
        ("C", "yet another option"),
        ))
    for level in utils.Log_level.__args__:
        with caplog.at_level(menu.logger.level(level).no):
            caplog.clear()
            m.show_options(opts, level)
            for log_message, (opt_key, opt_desc) in zip(caplog.messages, opts.items()):
                assert f"({opt_key})" in log_message
                assert f"{opt_desc}" in log_message


def test_show_reason(caplog):
    m = menu.Text_Menu("test menu", """Line 1\nLine 2\nLine 3""")
    reason = "Test reason"
    for level in utils.Log_level.__args__:
        with caplog.at_level(menu.logger.level(level).no):
            caplog.clear()
            m.show_reason(reason, level)
            assert reason in caplog.text


def test_show_comment(caplog):
    m = menu.Text_Menu("test menu", """Line 1\nLine 2\nLine 3""")
    for level in utils.Log_level.__args__:
        with caplog.at_level(menu.logger.level(level).no):
            caplog.clear()
            expected = "Test_comment"
            m.show_comment(expected, level)
            assert expected in caplog.text
