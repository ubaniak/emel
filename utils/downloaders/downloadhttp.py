import urllib2

from utils.downoaders.downloader import Downloader

class DownloadHTTP(Downloader):
    def __init__(self, src, dest):
        src = src if isinstance(src, list) else [src]
        dest = dest if isinstance(dest, list) else [dest]
        super(downloader, self).__init__(src,dest)
        
    def download(self):

        for s, d in zip(src, dest):
            f = urllib2.urlopen(s)
            

        pass
