#!/usr/bin/env python
#encoding:utf-8
#author:dbr/Ben
#project:themoviedb

"""An interface to the themoviedb.org API
"""

__author__ = "dbr/Ben"
__version__ = "0.1"

config = {}
config['apikey'] = "a8b9f96dde091408a03cb4c78477bd14"

config['urls'] = {}
config['urls']['movie.search'] = "http://api.themoviedb.org/2.0/Movie.search?title=%%s&api_key=%(apikey)s" % (config)

import urllib

import xml.etree.cElementTree as ElementTree

class TmdBaseError(Exception): pass
class TmdHttpError(TmdBaseError): pass
class TmdXmlError(TmdBaseError): pass

class XmlHandler:
    def __init__(self, url):
        self.url = url

    def _grabUrl(self, url):
        try:
            urlhandle = urllib.urlopen(url)
        except IOError:
            raise TmdHttpError(errormsg)
        return urlhandle.read()

    def getEt(self):
        xml = self._grabUrl(self.url)
        try:
            et = ElementTree.fromstring(xml)
        except SyntaxError, errormsg:
            raise TmdXmlError(errormsg)
        return et


class SearchResults(list):
    def __init__(self):
        super(SearchResults, self).__init__()
    def __repr__(self):
        return "<Search results: %s>" % (list.__repr__(self))


class Movie(dict):
    def __repr__(self):
        return "<Movie: %s>" % self.get("title")
        # return "<Movie: %s>" % (dict.__repr__(self))


class MovieAttribute(dict):
    pass


class Poster(MovieAttribute):
    """Stores poster image URLs, each size is under the approriate dict key.
    Common sizes are: cover, mid, original, thumb
    """
    def __repr__(self):
        return "<%s with sizes %s>" % (
            self.__class__.__name__,
            ", ".join(
                ["'%s'" % x for x in sorted(self.keys())]
            )
        )

    def set(self, poster_et):
        """Takes an elementtree Element ('poster') and stores the poster,
        using the size as the dict key.
        
        For example:
        <backdrop size="original">
            http://example.com/poster_original.jpg
        </backdrop>
        
        ..becomes:
        poster['original'] = 'http://example.com/poster_original.jpg'
        """
        size = poster_et.get("size")
        value = poster_et.text
        self[size] = value

    def largest(self):
        """Attempts to return largest image.
        """
        for cur_size in ["original", "mid", "cover", "thumb"]:
            if cur_size in self:
                return self[cur_size]

class Backdrop(Poster):
    """Stores backdrop image URLs, each size under the approriate dict key.
    Common sizes are: mid, original, thumb
    """
    pass

class MovieDb:
    def __init__(self):
        pass

    def _parseMovie(self, movie_element):
        cur_movie = Movie()
        cur_poster = Poster()
        cur_backdrop = Backdrop()
        for item in movie_element.getchildren():
            if item.tag.lower() == "poster":
                cur_poster.set(item)
            elif item.tag.lower() == "backdrop":
                cur_backdrop.set(item)
            else:
                cur_movie[item.tag] = item.text
        cur_movie['poster'] = cur_poster
        cur_movie['backdrop'] = cur_backdrop
        return cur_movie

    def search(self, title):
        url = config['urls']['movie.search'] % (title)
        etree = XmlHandler(url).getEt()
        search_results = SearchResults()
        for cur_result in etree.find("moviematches").findall("movie"):
            cur_movie = self._parseMovie(cur_result)
            search_results.append(cur_movie)
        return search_results


def search(name = None):
    """Searches for a film by its title.
    Returns SearchResults (a list) containing all matches (Movie instances)
    
    Wraps MovieDb.search method, so you can do
    >>> import tmd
    >>> tmd.search("A title")
    """
    mdb = MovieDb()
    return mdb.search(name)

def main():
    results = search("transformers")
    film = results[0]
    print(film.keys())
    print(film['id'])
    print(film['title'])
    print(film['short_overview'])
    print(film['backdrop'].largest())

if __name__ == '__main__':
    main()