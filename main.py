from StringIO import StringIO
import urllib2
import time
import lxml.html
import threading
# {TODO} http://stackoverflow.com/questions/5299968/download-several-parts-of-one-file-concurrently-with-python


class DivideAndDownload(object):
    """
    Takes a url to file as input, breaks the downloadable into chunks and parallely downloads
    then, stiches them into one.
    """

    def __init__(self, file_url, max_connections=4):
        self.file_url = file_url
        self.file_response = urllib2.urlopen(file_url)
        self.file_headers = dict(self.file_response.headers.items())
        self.accepts_parallel_connections = self.parallel_downloadable()
        self.file_size = self.get_file_size()
        self.no_of_connections = max_connections  # Left open for configuration
        try:
            self.chunk_size = self.file_size/self.no_of_connections  # Left open for configuration
        except:
            self.chunk_size = None
        self.chunks = {}
        self.threads = []

    def parallel_downloadable(self):
        """ Checks if `accept-ranges` in file url response headers """
        try:
            if self.file_headers['accept-ranges']:
                return True
            else:
                return False
        except KeyError:
            print(self.file_headers.keys())
            return False

    def get_file_size(self):
        """
        Returns the value of `content-length` from url response headers
        Returns `Unknown` if that key doesn't exist
        """
        try:
            return self.file_headers['content-length']
        except KeyError:
            print(self.file_headers.keys())
            return 'Unknown'

    def download_chunk(self, start_from):
        """ Downloads the chunk of file of size `self.chunk_size` from the `start_from` """
        request = urllib2.Request(self.file_url)
        request.headers['Range'] = 'bytes=%s-%s' % (start_from, start_from+self.chunk_size)
        f_read = urllib2.urlopen(request)
        self.chunks[start_from] = f_read.read()

    def parallel_download(self):
        """ Open `self.no_of_connections` threads and download as many chunks and stitch 'em together"""
        if self.parallel_downloadable() and self.chunk_size is not None:
            for i in range(self.no_of_connections):
                t = threading.Thread(target=self.download_chunk, args=(i*self.chunk_size))
                t.start()
                print("Reading a chunk of file")
                self.threads.append(t)
            for thread in self.threads:
                thread.join()
            result = ''
            for i in range(self.no_of_connections):
                result += self.chunks[i * self.chunk_size]
            return result
        else:
            return 'Error'

if __name__ == '__main__':
    base_url = raw_input('Enter URL >> ').strip()
    page_source = urllib2.urlopen(base_url)
    doc = lxml.html.parse(StringIO(page_source.read()))
    for each_link in doc.findall('.//a'):
        try:
            t = time.time()
            f_name = each_link.text
            if '480p' in f_name:
                mov = urllib2.urlopen(base_url+each_link.attrib['href'])
                with open('./Downloads/'+f_name, 'wb') as mov_disk:
                    try:
                        dd = DivideAndDownload(file_url=base_url+each_link.attrib['href'])
                        all_file = dd.parallel_download()
                        if all_file != 'Error':
                            mov_disk.write(all_file)
                        else:
                            print base_url+each_link.attrib['href']
                            print "Divide and download failed, switching to single thread download method."
                            raise Exception
                    except:
                        mov_disk.write(mov.read())
                    # TODO Use request.headers['accept-ranges'] to check if we can fire multiple requests
                    # to the server for downloading the file in parts. Use req.headers['content-length'] to
                    # divide evenly. How do you stich the parts back together after download?
                elapsed = time.time() - t
                print "Downloaded %s in %f minutes" % (f_name, elapsed/60.)
        except Exception as e:
            print "Exception at ", f_name, e

