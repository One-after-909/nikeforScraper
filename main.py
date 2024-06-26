from classes.scraper import ScraperCZ

import os
from dotenv import load_dotenv

load_dotenv()

scraper = ScraperCZ(db_connection=os.getenv("MONGO_DB_CONNECTION"), db_name=os.getenv("MONGO_DB_NAME"))

scraper.load_from_url(True)
scraper.save_to_file("./output/cz_bible.json")

# scraper.load_from_file("./output/cz_bible.json")
scraper.save_to_mongo()
