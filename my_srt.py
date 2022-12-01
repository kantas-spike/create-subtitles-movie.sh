from datetime import datetime, timedelta


def time_to_delta(t):
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)


def read_srt_file(path):
    item_list = []
    with open(path, encoding="utf-8") as f:
        item = {}
        for line in f:
            if len(line.rstrip()) == 0:
                if len(item) > 0:
                    item_list.append(item)
                    item = {}
            elif len(item) == 0:
                item['no'] = int(line)
            elif len(item) == 1:
                time_info = line.split("-->")
                if len(time_info) != 2:
                    raise ValueError(f"Bad time format:{item}")
                item['time_info'] = []
                for ti in time_info:
                    item['time_info'].append(time_to_delta(datetime.strptime(ti.strip(), "%H:%M:%S,%f")))
            elif len(item) == 2:
                item['lines'] = []
                item['lines'].append(line.rstrip())
            elif len(item) == 3:
                item['lines'].append(line.rstrip())

        if len(item) > 0:
            item_list.append(item)

    return item_list


def parse_line_of_time(line):
    pass