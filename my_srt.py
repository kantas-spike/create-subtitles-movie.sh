from datetime import datetime, timedelta
import json
import os
import re


def time_to_delta(t):
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)


def read_srt_file(path):
    item_list = []
    with open(path, encoding="utf-8") as f:
        item = {}
        for line_with_sep in f:
            line = line_with_sep.rstrip(os.linesep)
            if len(line) == 0:
                if len(item) > 0:
                    item_list.append(item)
                    item = {}
            elif len(item) == 0:
                item['no'] = int(line)
            elif len(item) == 1:
                if "-->" not in line:
                    raise ValueError(f"Bad time format:{item}")
                item['time_info'] = parse_line_of_time(line)
            elif len(item) == 2:
                item['lines'] = []
                item['lines'].append(line)
            elif len(item) == 3:
                item['lines'].append(line)

        if len(item) > 0:
            item_list.append(item)

    return item_list


def parse_line_of_time(line):
    m = re.match(r"\A(\d+:\d+:\d+,\d+) *--> *(\d+:\d+:\d+,\d+) *(.+)?", line)
    results = {}
    if m:
        for k, t in [["start", m.group(1)], ["end", m.group(2)]]:
            if t:
                results[k] = time_to_delta(datetime.strptime(t, "%H:%M:%S,%f"))
            else:
                results[k] = None
        if m.group(3):
            extras = m.group(3)
            if "JSON:" in extras:
                json_data = json.loads(extras.split("JSON:")[1].strip())
                # if "color" in json_data.keys():
                #     if type(json_data["color"]) is str:
                #         json_data["color"] = hex_to_rgba(json_data["color"])
                results["json"] = json_data
        return results
    else:
        return results


