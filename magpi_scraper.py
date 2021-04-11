import requests
import threading
from bs4 import BeautifulSoup

page_urls = []

def get_page_urls():
    """Retrieve all of the pages' URLs for download links and
    store them in a list(page_urls)"""

    url = 'https://magpi.raspberrypi.org/issues'
    res = requests.get(url)
    soup = BeautifulSoup(res.text,'html.parser')
    # Figure out number of pages needed to be scraped
    pagination_label = soup.select('.c-pagination__label')[0].get_text()
    num_of_pages = int(pagination_label.split(' ')[2])
    for i in range(1, num_of_pages+1):
        URL = f"https://magpi.raspberrypi.org/issues?page={i}"
        page_urls.append(URL)

def downloadMagPi(URL):
    """Gets urls for each issue on current page and writes them to disk"""
    BASEURL = 'https://magpi.raspberrypi.org'

    # List that holds urls to each issues download page
    download_urls = []
    # List that holds urls to each issues pdf file
    pdf_urls = []

    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')

    # Iterate through every <a> tag on the page and find download urls
    # and append them to download_urls
    for a in soup.find_all('a'):
        href = a['href']
        if a.text == 'Download Free PDF' or a.text == 'Free Download':
            downloadLink = BASEURL + href + '/download'
            download_urls.append(downloadLink)

    for link in download_urls:
        downloadPage = requests.get(link)
        bs = BeautifulSoup(downloadPage.text, 'html.parser')
        # Iterate through every <a> tag to get actual pdf download link
        # and append to pdf_urls
        for a in bs.select('a'):
            if a.text == 'click here to get your free PDF':
                pdf_link = a['href']
                pdf_url = BASEURL + pdf_link
                pdf_urls.append(pdf_url)

    for file in pdf_urls:
        fileName = file.split('/')[-1]
        # Download the file
        fileRequest = requests.get(file)
        with open(fileName, 'wb') as issueFile:
            issueFile.write(fileRequest.content)

get_page_urls()
for url in page_urls:
    processThread = threading.Thread(
        target=downloadMagPi, args=(url,))
    processThread.start()
