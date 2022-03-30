import html
import calendar
from pandas import DataFrame
from datetime import datetime
from tinydb import TinyDB
from tinydb.table import Document, Table
from Scweet.scweet import scrape


def get_lastday_of_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def get_tweets_df(
    user_id: str,
    since: str,
    until: str,
    interval: int,
    headless: bool = False,
    display_type: str = "Top",
) -> DataFrame:
    df = scrape(
        from_account=user_id,
        since=since,
        until=until,
        interval=interval,
        headless=headless,
        display_type=display_type,
    )
    return df


def df_to_csv(df: DataFrame) -> str:
    return df.to_csv()


def get_yyyy_mm_dd(year: int, month: int, day: int) -> str:
    dt = datetime(year, month, int)
    return dt.strftime("%Y-%m-%d")


def get_db(json_path: str) -> TinyDB:
    db: TinyDB = TinyDB(json_path)
    return db


def get_table(db: TinyDB, table_name: str) -> Table:
    return db.table(table_name)


def timestamp_to_int(timestamp: str) -> int:
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    i = int(dt.timestamp())
    return i


def insert_df(table: Table, df: DataFrame) -> None:
    for idx, row in df.iterrows():

        try:
            timestamp: str = row["Timestamp"]
        except:
            print(f"Not found Timestamp in row")
            continue

        try:
            timestamp_int: int = timestamp_to_int(timestamp)
        except:
            print(f"Invalid Timestamp ({timestamp})")
            continue

        try:
            doc: Document = Document(
                {
                    "UserScreenName": row["UserScreenName"],
                    "UserName": row["UserName"],
                    "Timestamp": row["Timestamp"],
                    "Text": row["Text"],
                    "EmbeddedText": row["Embedded_text"],
                    "Emojis": row["Emojis"],
                    "Comments": row["Comments"],
                    "Likes": row["Likes"],
                    "Retweets": row["Retweets"],
                    "ImageLink": row["Image link"],
                    "TweetUrl": row["Tweet URL"],
                },
                doc_id=timestamp_int,
            )
            table.insert(doc)
        except ValueError:
            print(f"InsertTweet: {timestamp} Failed")
            continue
        except AssertionError:
            print(f"InsertTweet: {timestamp} Already => Skip")
            continue
        print(f"InsertTweet: {timestamp} {cleanup_embedded_text(row['Embedded_text'])}")


def cleanup_embedded_text(embedded_text: str) -> str:
    tokens = embedded_text.split("\n")
    result = ""
    for idx, token in enumerate(tokens):
        if token == "":
            continue
        if is_int_str(token):
            continue
        if idx != 0:
            result += "\n"
        result += token
    return result


def is_int_str(s: str) -> bool:
    try:
        i = int(s)
    except:
        return False
    return True


def crawl_all_tweets_to_table(user_id: str, table: Table) -> None:
    now = datetime.now()
    start_year = 2009
    current_year = now.year
    for year in range(start_year, current_year + 1):
        for month in range(1, 13):
            since = f"{year}-{str(month).zfill(2)}-01"
            until = f"{year}-{str(month).zfill(2)}-{str(get_lastday_of_month(year,month)).zfill(2)}"
            interval = 15
            print(f"* Since:{since} Until:{until} Interval:{interval}")
            df = get_tweets_df(
                user_id=user_id, since=since, until=until, interval=interval
            )
            insert_df(table, df)


def row_to_html(row) -> str:
    result: str = ""

    timestamp = timestamp_to_int(row["Timestamp"])
    dt = datetime.fromtimestamp(timestamp)
    user_id: str = row["UserScreenName"]
    datetime_str: str = dt.strftime("%Y-%m-%d %H:%M:%S")
    text: str = cleanup_embedded_text(row["EmbeddedText"])
    text = html.escape(text)
    text = text.replace("\n", "<br/>\n")

    result += f"\t\t<article id='{timestamp}' class='twt_card'>\n"
    result += f"\t\t\t<div class='twt_text'>{text}</div>\n"
    result += (
        f"\t\t\t<div class='twt_info'>{user_id} | {html.escape(datetime_str)}</div>\n"
    )
    result += "\t\t</article>\n"

    return result


def crawl_demo(user_id: str) -> None:
    db: TinyDB = get_db(json_path=f"{user_id}.json")
    table = get_table(db=db, table_name="tweets")
    crawl_all_tweets_to_table(user_id=user_id, table=table)


def export_html_demo(filepath: str, user_id: str) -> None:
    db: TinyDB = get_db(json_path=f"{user_id}.json")
    table: Table = get_table(db=db, table_name="tweets")
    title: str = f"{user_id} Tweets"

    header: str = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="description" content="{user_id} All Tweets">
        <meta name="keywords" content="twitter, crawl, all">
        <meta name="author" content="{user_id}">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="styles.css">
        <script src="scripts.js" user_id="{user_id}"></script>
        <title>{title}</title>
    </head>
    <body>
        <header>
            <h1>{title}</h1>
        </header>
        <div id="articles">
    """

    now_dt = datetime.now()
    footer: str = f"""
        <footer>
            <div>{now_dt.year} {user_id} All rights reserved.</div>
        </footer>
    </body>
    </html>
    """

    with open(filepath, "w", encoding="utf8") as f:
        f.write(header)
        sorted_rows = sorted(
            table.all(), key=lambda row: row["Timestamp"], reverse=True
        )
        for row in sorted_rows:
            f.write(row_to_html(row))
        f.write(footer)


if __name__ == "__main__":
    export_html_demo("TWTUSER.html", "TWTUSER")
