import os
BASE_DIR = os.path.dirname(__file__)

if __name__ == "__main__":
    while True:
        os.system(f'python {os.path.join(BASE_DIR, "scraper", "polling", "get_active_links.py")}')
        os.system(f'python {os.path.join(BASE_DIR, "scraper", "polling", "start_update.py")}')
