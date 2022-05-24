import requests
from bs4 import BeautifulSoup as bs
from pythonfuzz.main import PythonFuzz

@PythonFuzz
def fuzz(buf):
	try:
		string = buf.decode("ascii")

		page = requests.get("https://library.gabia.com/")
		soup = bs(page.text, "html.parser")

		elements = soup.select('div.esg-entry-content a > span')
	except UnicodeDecodeError:
		pass

if __name__ == '__main__':
	fuzz()


