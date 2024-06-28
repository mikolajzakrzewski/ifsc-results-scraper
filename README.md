# IFSC Results Scraper

Program for scraping climbing competition results from the official website of the International Federation of Sport Climbing (https://ifsc-climbing.org) using **scrapy** and its **Spider** class. Scraped data is saved to a local SQLite database and a csv file with a timestamp.

### Disclaimer:

Always ensure compliance with the website's terms of service and any legal requirements related to web scraping and data usage.

## Run Locally

Clone the project

```bash
  git clone https://github.com/mikolajzakrzewski/ifsc-results-scraper.git
```

Go to the project directory

```bash
  cd ifsc-results-scraper
```

Install packages

```bash
  pip install -r requirements.txt
```

Go to the scrapy project directory

```bash
  cd ifsc_scraper
```

Run the program

```bash
scrapy crawl -a years=<years> -a disciplines=<discipline_codes> -a categories=<category_codes> ifsc_climbing_org
```

parameters' definition:

```bash
<years> = comma-separated years

<discipline_codes> = comma-separated discipline codes

<category_codes> = comma-separated category codes
```

allowed parameters' values:

```bash
years: 1990-2024

discipline_codes:
    "l": "lead",
    "s": "speed",
    "b": "boulder",
    "c": "combined",
    "bl": "boulder&lead"

category_codes:
    "m": "men",
    "w": "women",
    "yam": "youth a male",
    "yaf": "youth a female",
    "ybm": "youth b male",
    "ybf": "youth b female",
    "jm": "juniors male",
    "jf": "juniors female"
```

### Example execution

Scrape the men's and women's speed climbing results from the years 2014 to 2023:

```bash
scrapy crawl -a years=2014,2015,2016,2017,2018,2019,2020,2021,2022,2023 -a disciplines=s -a categories=m,w ifsc_climbing_org
```

## Authors

- [@mikolajzakrzewski](https://github.com/mikolajzakrzewski)


## License

[MIT](https://choosealicense.com/licenses/mit/)

