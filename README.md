# IFSC Results Scraper

Program for scraping climbing competition results from the IFSC Climbing Result Service website (https://ifsc.results.info) using **scrapy** and its **Spider** class

### Disclaimer:

**Legitimate Interest**: This scraper gathers data for research purposes, specifically to analyze climbing competition results for statistical and performance analysis. The legitimate interest for collecting and processing this data includes contributing to the understanding of sports performance, improving training methodologies, and enhancing the overall experience of climbing athletes and enthusiasts.

It is essential to handle the scraped data in accordance with applicable data protection laws, including GDPR, and to respect the privacy rights of individuals whose data may be included in the competition results.

**Note**: Always ensure compliance with the website's terms of service and any legal requirements related to web scraping and data usage.

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
scrapy crawl -a years=<years> -a leagues=<league_codes> -a disciplines=<discipline_codes> -a categories=<category_codes> ifsc_results_info -o <output_file>
```

parameters' definition:

```bash
<years> = comma-separated years

<league_codes> = comma-separated league codes

<discipline_codes> = comma-separated discipline codes

<category_codes> = comma-separated category codes

<output_file> = .csv or .json file to write the scraped data into
```

allowed parameters' values:

```bash
years: 1990-2024

league_codes:
    "wc": "World Cups and World Championships",
    "y": "IFSC Youth",
    "pc": "IFSC Paraclimbing (L)",
    "aa": "IFSC Asia Adults",
    "ay": "IFSC Asia Youth",
    "ey": "IFSC Europe Youth",
    "pa": "IFSC Panam",
    "oc": "IFSC Oceania",
    "g": "Games",
    "oe": "Other events",
    "m": "Masters and Promotional Events"

discipline_codes:
    "l": "lead",
    "s": "speed",
    "b": "boulder",
    "c": "combined",
    "bl": "boulder&lead"

category_codes:
    "m": "Men",
    "w": "Women",
    "yam": "Youth A Male",
    "yaf": "Youth A Female",
    "ybm": "Youth B Male",
    "ybf": "Youth B Female",
    "jm": "Juniors Male",
    "jf": "Juniors Female"
```

### Example execution

```bash
scrapy crawl -a years=2013 -a leagues=wc -a disciplines=s -a categories=m ifsc_results_info -o results.csv
```

## Authors

- [@mikolajzakrzewski](https://github.com/mikolajzakrzewski)


## License

[MIT](https://choosealicense.com/licenses/mit/)

