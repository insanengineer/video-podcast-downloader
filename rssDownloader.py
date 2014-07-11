import feedparser
import urllib
import sys
import os.path

#ToDo:
#  save a file that is formated to give the correct info to xbmc or plex for video meta info

# global settings
maxFeedDownLoads = 1
downloadFeedImage = 0

# function to utilize the reporthook if urllib
# this allows us to get the requred information and display download progress of
# the large file
def fileDownloadProgress(count, blockSize, totalSize):
    percent = int(count * blockSize * 100 / totalSize)
    sys.stdout.write("Downloading " + fileName + " %d%% remaining  \r" % percent)
    sys.stdout.flush()

# this array is intended to hold all the Rss Feed URLs to parse for download
rssFeedUrlList = []

# get the settings from the config file
with open('rssDownloader.conf') as configFile:
    # read the contents of the file into an array
    configFileContents = configFile.readlines()

    # clean up the array to remove all the new line elements
    for a in configFileContents:

        # split on the new line element
        newData = a.split('\n') [0]

        # get the index of the current array element
        currentIndex = configFileContents.index(a)

        # remove the old element from the array
        configFileContents.remove(a)

        # put in the modified data back in were it was removed
        configFileContents.insert(currentIndex, newData)

    # get the index of the feed url header
    feedUrlIndex = configFileContents.index('[Feed URLs]')

    # get the index of the begining of the next section
    settingsIndex = configFileContents.index('[Settings]')

    # populate the rss feed url array so we can download all the items
    for x in range(int(feedUrlIndex + 1), int(settingsIndex - 1)):
        rssFeedUrlList.append(configFileContents[x])

    # get the flag for downloading rss feed image from the config file
    maxFeedDownLoads = int(configFileContents[(settingsIndex + 1)].split('=') [1])

    # get the max number of feeds to download from the config file
    downloadFeedImage = int(configFileContents[(settingsIndex + 2)].split('=') [1])

# download the newwst file from each rss feed
for currentFeed in rssFeedUrlList:

    urlPathElement = currentFeed.split(' ')

    url = urlPathElement[0]
    filePath = urlPathElement[1]

    # parse the rss feed from the specified url
    rssFeed = feedparser.parse(url)

    # if the user want the feed image download it
    if downloadFeedImage == 1:
        # the url of the image representing the feed
        feedImageUrl = rssFeed.feed.image.href

        # split the download url so we can get the last item which should contain the
        # file name
        feedImageName = filePath + feedImageUrl.split('/') [-1]

        # download the file from the url
        urllib.request.urlretrieve(feedImageUrl, feedImageName)

    # get the number of feeds set by the user
    for numOfFeeds in range(0, maxFeedDownLoads):

        feedTitle = rssFeed.entries[numOfFeeds].title
        feedDescription = rssFeed.entries[numOfFeeds].description

        # the variable that holds the download link for the podcast
        dlLInk = rssFeed.entries[numOfFeeds].enclosures[numOfFeeds].href

        # split the download url so we can get the last item which should contain the
        # file name
        fileName = filePath + dlLInk.split('/') [-1]

        #check if the directory exists. if it does not exist then create it
        if not os.path.exists(filePath):
            os.makedirs(filePath)

        # check if the file already exists
        if not os.path.isfile(fileName):
            # download the file from the url if the file does not exist
            urllib.request.urlretrieve(dlLInk, fileName, reporthook=fileDownloadProgress)
