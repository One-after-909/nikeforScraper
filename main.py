from classes.scraper import ScraperCZ

scraper = ScraperCZ()

# scraper.load_from_url(True)
scraper.load_from_file("./cz/headers.json")
scraper.save_to_file("./output/bible_cz_clp.json")
