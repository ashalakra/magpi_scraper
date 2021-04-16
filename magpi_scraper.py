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

    # COMMENT:
    #
    # You could call `object.split()[-1]`. This always gets the last
    # object in a list, but if the list is empty then you will get an
    # `IndexError`.  The same goes for `object.split()[2]` if the list
    # is empty.
    #
    # For a small project like this, what you have is fine, but if
    # it's a list that can change in size everytime you get it, then
    # you might want to check the size of the list before trying to
    # extract from a position.
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

# Begin threading process

# COMMENT:
#
# If I understand this correctly, are you creating a thread for each
# page and then having each thread download all the pdfs on its
# particular page?
#
# This works, but if there are a lot of pages then you will spawn a
# lot of threads. You have to be careful you don't create a denial of
# service (DOS) attack unintentionally to a website.
#
# Sometimes a simple loop on the main thread works just fine and maybe
# even faster depending on your computer and the website.
for url in page_urls:
    processThread = threading.Thread(
        target=downloadMagPi, args=(url,))
    processThread.start()
