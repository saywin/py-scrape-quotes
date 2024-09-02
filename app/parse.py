import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup


URL = "https://quotes.toscrape.com/"
QUOTE_OUTPUT_CSV_PATH = "quotes.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def get_list_quotes(soup: BeautifulSoup) -> [Quote]:
    all_quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in all_quotes]


def get_page_number() -> int:
    url = URL
    page_number = 1

    while True:
        page = requests.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        next_button = soup.select_one(".next > a")
        if next_button:
            page_number += 1
            url = URL + next_button["href"]
        else:
            break
    return page_number


def get_quotes() -> [Quote]:
    page = requests.get(URL).content
    first_page_quotes = BeautifulSoup(page, "html.parser")
    all_quotes = get_list_quotes(first_page_quotes)

    page_numbers = get_page_number()

    for page_num in range(2, page_numbers + 1):
        page = requests.get(URL + f"/page/{page_num}/").content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(
            get_list_quotes(soup)
        )
    return all_quotes


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def write_quites_to_csv(quotes: [Quote]) -> None:
    with open(QUOTE_OUTPUT_CSV_PATH, "w", encoding="utf8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        for quote in quotes:
            writer.writerow([quote.text, quote.author, ", ".join(quote.tags)])


def main(output_csv_path: str) -> None:
    write_quites_to_csv(get_quotes())


if __name__ == "__main__":
    main("quotes.csv")
