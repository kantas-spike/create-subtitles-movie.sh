from datetime import timedelta
import my_srt
import os
import pytest


@pytest.fixture(scope="session")
def json_srt_file_01(tmp_path_factory):
    content = """1
00:00:05,0 --> 00:00:25,0 JSON: {"location": [0, -1, 0]}
アメンボ赤いな
"""
    f_path = tmp_path_factory.mktemp("data") / "json01.srt"
    with open(f_path, mode="w+t") as f:
        f.write(content)
    return f_path


@pytest.fixture(scope="session")
def simple_srt_file_01(tmp_path_factory):
    content = """1
00:00:05,0 --> 00:00:25,0
アメンボ赤いな
"""
    f_path = tmp_path_factory.mktemp("data") / "simple01.srt"
    with open(f_path, mode="w+t") as f:
        f.write(content)
    return f_path


@pytest.fixture(scope="session")
def simple_srt_file_06(tmp_path_factory):
    content = """1
00:00:05,0 --> 00:00:25,0
アメンボ
赤いな



2
00:00:07,26 --> 00:00:25,0
アイウエオ

3
00:00:09,27 --> 00:00:25,0
浮藻にコエビも泳いでる

4
00:00:12,30 --> 00:00:25,0
柿の木、栗の木

5
00:00:15,3 --> 00:00:25,0
カキクケコ

6
00:00:17,8 --> 00:00:25,0
キツツキこつこつ枯れケヤキ

"""
    f_path = tmp_path_factory.mktemp("data") / "simple.srt"
    with open(f_path, mode="w+t") as f:
        f.write(content)
    return f_path


def assert_srt_item(item, no, start_sec, end_sec, contain_str, json=None):
    __tracebackhide__ = True
    assert no == item["no"]
    assert timedelta(seconds=start_sec) == item["time_info"]["start"]
    assert timedelta(seconds=end_sec) == item["time_info"]["end"]
    assert contain_str in str.join(os.linesep, item["lines"])
    if json is None:
        assert "json" not in item.keys()
    else:
        assert json == item["time_info"]["json"]


class TestHexToRGBA:
    def test_hex_to_rgba_with_rgba(self):
        assert [10 / 0xFF, 11 / 0xFF, 12 / 0xFF, 13 /
                0xFF] == my_srt.hex_to_rgba("#0a0b0c0d")
        assert [10 / 0xFF, 11 / 0xFF, 12 / 0xFF, 13 /
                0xFF] == my_srt.hex_to_rgba("#0A0B0C0D")
        assert [10 / 0xF, 11 / 0xF, 12 / 0xF, 13 /
                0xF] == my_srt.hex_to_rgba("#abcd")
        assert [10 / 0xF, 11 / 0xF, 12 / 0xF, 13 /
                0xF] == my_srt.hex_to_rgba("#ABCD")

        assert [1, 1, 1, 1] == my_srt.hex_to_rgba("#FFFFFFFF")
        assert [1, 1, 1, 1] == my_srt.hex_to_rgba("#FFFF")
        assert [0, 0, 0, 0] == my_srt.hex_to_rgba("#00000000")
        assert [0, 0, 0, 0] == my_srt.hex_to_rgba("#0000")

    def test_hex_to_rgba_with_rgb(self):
        assert [10 / 0xFF, 11 / 0xFF, 12 / 0xFF,
                1] == my_srt.hex_to_rgba("#0a0b0c")
        assert [10 / 0xFF, 11 / 0xFF, 12 / 0xFF,
                1] == my_srt.hex_to_rgba("#0A0B0C")
        assert [10 / 0xF, 11 / 0xF, 12 / 0xF, 1] == my_srt.hex_to_rgba("#abc")
        assert [10 / 0xF, 11 / 0xF, 12 / 0xF, 1] == my_srt.hex_to_rgba("#ABC")

        assert [1, 1, 1, 1] == my_srt.hex_to_rgba("#FFFFFF")
        assert [1, 1, 1, 1] == my_srt.hex_to_rgba("#FFF")
        assert [0, 0, 0, 1] == my_srt.hex_to_rgba("#000000")
        assert [0, 0, 0, 1] == my_srt.hex_to_rgba("#000")


class TestReadSrtFile:
    def test_read_simple_srt_file_01(self, simple_srt_file_01):
        results = my_srt.read_srt_file(simple_srt_file_01)
        assert 1 == len(results)
        assert_srt_item(results[0], 1, 5.0, 25.0, "アメンボ赤いな")

    def test_read_simple_srt_file_06(self, simple_srt_file_06):
        results = my_srt.read_srt_file(simple_srt_file_06)
        assert 6 == len(results)
        assert_srt_item(results[0], 1, 5.0, 25.0, f"アメンボ{os.linesep}赤いな")
        assert_srt_item(results[1], 2, 7.26, 25.0, "アイウエオ")
        assert_srt_item(results[2], 3, 9.27, 25.0, "浮藻にコエビも泳いでる")
        assert_srt_item(results[3], 4, 12.30, 25.0, "柿の木、栗の木")
        assert_srt_item(results[4], 5, 15.3, 25.0, "カキクケコ")
        assert_srt_item(results[5], 6, 17.8, 25.0, "キツツキこつこつ枯れケヤキ")

    def test_read_json_srt_file_01(self, json_srt_file_01):
        results = my_srt.read_srt_file(json_srt_file_01)
        assert 1 == len(results)
        assert_srt_item(results[0], 1, 5.0, 25.0,
                        "アメンボ赤いな", {"location": [0, -1, 0]})


class TestParseLineOfTime:
    def test_simple_line(self):
        results = my_srt.parse_line_of_time("00:20:41,150  --> 00:20:45,109")
        assert 2 == len(results)
        assert timedelta(hours=0, minutes=20, seconds=41,
                         milliseconds=150) == results["start"]
        assert timedelta(hours=0, minutes=20, seconds=45,
                         milliseconds=109) == results["end"]

    def test_line_with_extras(self):
        results = my_srt.parse_line_of_time(
            "00:20:41,150  --> 00:20:45,109 X1:100")
        assert 2 == len(results)
        assert timedelta(hours=0, minutes=20, seconds=41,
                         milliseconds=150) == results["start"]
        assert timedelta(hours=0, minutes=20, seconds=45,
                         milliseconds=109) == results["end"]

    def test_line_with_json(self):
        results = my_srt.parse_line_of_time(
            "00:20:41,150  --> 00:20:45,109 JSON:{\"location\": [0, -1, 0]}")
        assert 3 == len(results)
        assert timedelta(hours=0, minutes=20, seconds=41,
                         milliseconds=150) == results["start"]
        assert timedelta(hours=0, minutes=20, seconds=45,
                         milliseconds=109) == results["end"]
        assert {"location": [0, -1, 0]} == results["json"]
