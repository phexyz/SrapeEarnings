import bs4
import urllib.request
import json
import re
import datetime
import pandas as pd

def fetch_html(symbol):

    url = "https://www.zacks.com/stock/research/{}/earnings-announcements".format(symbol)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    request = urllib.request.Request(url, headers=headers)
    html = urllib.request.urlopen(request)
    htmlFile = html.read().decode()
    html.close()

    with open("{}.html".format(symbol), "w") as f:
        f.write(htmlFile)

    soup = bs4.BeautifulSoup(htmlFile)

    earningsTable = soup.find("section", {"id":"earnings_announcements_tabs"}).next_sibling.contents[0]
    for i in range(5):
        print()
    earningsContent = earningsTable.replace("\n", "")
    earningsString = re.search("{.*}", earningsContent)[0]
    earningsJSON = json.loads(earningsString)

    with open("./{}_earnings_table.json".format(symbol), "w") as f:
        json.dump(earningsJSON, f, indent=4)

    return earningsJSON

def convert_json_to_dataFrame(symbol):

    try:
        with open("./{}_earnings_table.json".format(symbol), "r") as f:
            earningsJSON = json.load(f)
    except FileNotFoundError:
        earningsJSON = fetch_html(symbol)

    key = "earnings_announcements_earnings_table"
    for row in earningsJSON[key]:

        row[0] = datetime.datetime.strptime(row[0], "%m/%d/%Y")
        row[1] = datetime.datetime.strptime(row[1], "%m/%Y")

        for i in range(2,4):
            extractedText = re.findall("(.*)\$(.*)", row[i])
            row[i] = float("".join(extractedText[0])) if extractedText else None

        extractedText = re.findall(">(.*)<", row[4])
        row[4] = float(extractedText[0]) if extractedText else None

        if row[5]:
            extractedText = re.findall(">([0-9]*),?([0-9]*)%<", row[5])
            row[5] = float("".join(extractedText[0])) / 100 if extractedText else None

    earningsDF = pd.DataFrame(earningsJSON[key], columns=["date", "period_ending", "estimate",
                                             "reported", "surprise", "%surprise",
                                             "time"])

    earningsDF.to_csv("./{}_dataFrame.csv".format(symbol))
    return earningsDF

if __name__ == '__main__':
    fetch_html("TSLA")