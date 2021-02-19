import scraper
from dotenv import load_dotenv


def main():
    load_dotenv()
    # urls = ['https://www.marketwatch.com/latest-news', 'https://www.marketwatch.com/markets',
    #         'https://www.marketwatch.com/investing']
    urls = ['https://www.marketwatch.com/latest-news', 'https://seekingalpha.com/market-news']
    keywords = ['bitcoin', 'crypto', 'spac', 'gains', 'ghvi', 'merger', 'fda', 'archer', 'approval', 'asia', 'asian',
                'nio', 'earnings', 'ev', 'electric vehicle', 'sell', 'acquire', 'acquisition', 'etf', 'startup',
                'start-up', 'energy', 'green', 'deal', 'contract', 'ark', 'ark invest', 'cathie wood']
    s = scraper.Scraper(keywords)
    s.start_db_clear_timer()
    s.start(urls)


if __name__ == "__main__":
    main()
