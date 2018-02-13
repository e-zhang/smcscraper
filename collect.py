import datetime
import json
import requests

SPD_URL = "https://data.seattle.gov/resource/y7pv-r3kh.json?offense_code={}&$order=:id&$offset={}&$limit={}"

DATETIME_FMT = "%Y-%m-%dT%H:%M:%S.%f"
PROSTITUTION_OFFENSE_CODE = "4099"
GO_OFFSET = 2000000000


def fetch(load_json=False, save_json=False):
    ''' 
        Fetch json data from SPD API
        @param load_json alternatively loads data from a presaved json file
        @param save_json optionally saves fetched data to a json file
    ''' 
    if load_json:
        data = json.load(open('spd.json'))
        return data

    offset = 0
    limit = 50000
    data = []
    while True:
        r = requests.get(SPD_URL.format(PROSTITUTION_OFFENSE_CODE, offset, limit))
        d = r.json()
        if len(d) == 0:
            break
        data.extend(d)
        offset += len(d)

    if save_json:
        json.dump(data, open('spd.json', 'w'), indent=2)


def get_go_nums():
    '''
        Fetches and formats General Offense Numbers for use with SMC portal
    '''
    data = fetch()
    incidents = filter(lambda x: x["offense_code"] == PROSTITUTION_OFFENSE_CODE, data)
    incidents = sorted(incidents, key=lambda x: datetime.datetime.strptime(x["date_reported"], DATETIME_FMT))
    go_nums = set()
    for x in incidents:
        if len(x["general_offense_number"]) != 10:
            continue
        go_smc = int(x["general_offense_number"]) - GO_OFFSET
        go_smc = str(go_smc)
        go_nums.add('-'.join((go_smc[:2], go_smc[2:])))

    return list(go_nums)
