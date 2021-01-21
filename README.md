# RISJbot
A scrapy project to extract the text and metadata of articles from news
websites.

This should provide much of the structure and parsing code needed to fetch
from arbitrary news websites. It may work out-of-the-box on some or more of
the sites with specific spiders already written (see below) but be aware that
web scrapers are by their nature somewhat brittle: they depend on the
underlying format and structure of each site's pages, and when these are
changed they tend to break. Although RISJbot has a fallback scraper that does
a reasonable job with arbitrary news pages, it's not a substitute for a
hand-tailored spider.

Having some degree of experience with Python would be very helpful. If sites
update their templates or you want to add a new site to the collection then
some coding will be necessary. I've tried to ensure that the existing code
is well commented. The Scrapy docs are themselves quite good if you find
yourself needing to understand what is going on behind the scenes.

You should be aware that this was written to support the author's academic
research into online news. It is still actively (if slowly) developed
for that purpose, but it is not production-level code and comes with even
fewer guarantees than most Free software.


## Installation

This is a Scrapy project, so first you need a working Scrapy installation:
https://docs.scrapy.org/en/latest/intro/install.html

The second thing to do is to clone RISJbot and edit `settings.py` to set things
up how you want them. The example settings file does most things sensibly.
Make sure you set up a sensible place for the crawl data to be put.

Third, customise a crawler for the site you want to scrape. There are some
working examples in the project, so the 'guardian' crawler fetches articles
from Britain's *The Guardian*, for example.

Fourth, use pip to install the dependencies in `requirements.txt` (currently
specific versions of `dateparser`, `extruct`, `textblob`, `pronouncing`,
`scrapy-dotpersistence`, `scrapy-splash` and `readability-lxml`.

The final thing is to run the crawler: `scrapy crawl guardian` will fetch
its way through *The Guardian*. But at this point it's basically an ordinary
Scrapy installation, and the regular Scrapy docs should see you through.

Output will be sent in JSONLines format to the S3 bucket you configured in
`settings.py`, or (if you haven't given credentials) to a `jsonloutput`
directory in the current directory.

If you want to load your output data into an R-based analysis framework via the
`tm` package, there is a companion package
[`tm.plugin.risjbot`](https://github.com/pmyteh/tm.plugin.risjbot) which does
this easily. From there it's straightforward to convert it for use with
`quanteda`, a more modern (and more actively maintained) R-based ecosystem.
JSONLines libraries are also readily available for other programming languages
and workflows.


## Spiders

This project contains a number of scrapy spiders to extract data from specific
US and UK websites:
* ABC
* ~~AP~~ [currently non-functional]
* BBC
* Bild
* Business Insider (US, DE, and FR)
* Buzzfeed (US and UK, plus a global feed)
* CBS
* CNN
* Daily Mail
* Fox News
* Guardian
* Huffington Post (US, ~~UK~~, and FR) [UK currently non-functional]
* Independent
* Liverpool Echo [including experimental comment scraping support]
* Metro
* Mirror
* NBC
* New York Times
* PR Newswire (US and UK)
* Reuters
* Sun
* Telegraph
* USA Today
* Vice (US, UK, DE, and FR. These are experimental, and require a configured
Splash headless browser instance, with a suitable `SPLASH_URL` configured in
`settings.py`. See `spiders/base/vice.py` for details.)
* Washington Post
* Yahoo! (US)

Page formats change, so not all of these spiders may be currently operational.
RISJbot now has a fallback text extractor using the readability library which
may help a bit. Nevertheless, pull requests to fix spider brokenness are most
welcome.

Do also be aware that there are some geographical issues that can be run into.
USA Today, for example, provides a different site for users geolocated to the
EU, which means that a working crawler can stop working when your computer
moves.

The source of URLs to crawl is generally either a public RSS feed of new
articles, or the sitemaps published to alert Google News of the articles
available. You may be able to find suitable feeds through the
[feed_seeker package](https://github.com/mitmedialab/feed_seeker).

As an alternative, it's possible to crawl a specified list of URLs from a
file. This is implemented in the NewsSpecifiedSpider class; see
`spiders/uk/guardian.py` for a working example.

A spider class is also available for doing a link-following crawl via Splash
(a headless browser which allows JavaScript-heavy pages to be properly
handled).

## Middlewares and extensions
In addition to the spiders, there are a number of interesting new pieces of
middleware and extensions which expand crawling possibilities for this and
other projects:

### FlexibleDotScrapyPersistence
An extension for projects hosted on ScrapingHub, using a hacky subclassing of
DotScrapyPersistence to allow persistent content to be stored in an arbitrary
S3 bucket rather than in ScrapingHub's own.

### RefetchControl
This is a spider middleware to ignore requests to pages containing items
seen in previous crawls of the same spider. It is a modified version of
http://github.com/scrapy-deltafetch/DeltaFetch v1.2.1.

RefetchControl differs from the parent DeltaFetch by offering more general
control over repeated fetching:
* The option of fetching (limited numbers of) copies of an item, 
  at intervals of not less than a given time. This allows some sane change
  detection.
* A mechanism for ensuring complete fetches, by trawling RefetchControl's
  database for insufficiently-fetched pages and scheduling them.

Depends on sqlite3 instead of bsddb3.

### EquivalentDomains
Spider middleware to coerce sets of equivalent domains to a single
canonical location. This can deal with situations like
http://editions.cnn.com and http://www.cnn.com, which deliver identical
content. Should be put early in the chain.

### ExtractJSONLD
Spider middleware to extract JSON-LD blocks and save their data into the
Response's meta tag. This stops them being squelched by <script>-killing
code and makes them easier to extract from.

### Fake404
Spider middleware to drop pages iff they are that annoyance on the web:
the 404 'not found' response returned as a branded page with HTTP code
200 (which should indicate success).

This should not be necessary, both because such behaviour is improper
on behalf of webservers, and because we are literally crawling the
sites' OWN LIST OF VALID PAGES. Nevertheless, foxnews.com does it and
others might.

### UnwantedContent
Spider middleware to process a response's selector by removing a
(configurable) set of elements from it. This is used to strip things
like figures from the content before passing the body on to the parsing
code. This makes it feasible to strip similar junk from all pages if
necessary.

Note that this leaves response.selector and response.body containing
different data. This is (1) an advantage, as it lets the spider save
the original page, and (2) a disadvantage, as the 'response' object
is confusingly no longer coherent. Caller beware!

Under the covers, Selectors contain an lxml.etree.Element document
root, which is not exposed by the Selector interface. This is mutatable
using the .remove method on parts of the selector.root document tree.
Unfortunately, there is no native content removal interface in scrapy.

As this is not using a published interface for Selector, it must be
considered risky. In particular, it is feasible (though not likely) that
scrapy could change its selector implementation to use a different
HTML/XML parsing library, at which point this would fail.

### OffsiteDownloaderShim
This is a shim to adapt the existing OffsiteMiddleware spider
middleware as downloader middleware. This lets it properly discard
offsite redirects from non-spider sources (such as those generated
from the independent.co.uk sitemap.

See https://github.com/scrapy/scrapy/issues/2241

A grotty hack, but a useful one.

### StripNull
Downloader middleware to discard ASCII NUL bytes from Responses. This
really(!) shouldn't be necessary, but bigstory.ap.org/latest (and
possibly other pages from bigstory.ap.org) are studded with NUL bytes,
which really messes up the underlying lxml parsing library (which is
C based and presumably uses null-terminated strings). The effect is that
the page's parse tree is cut off where the NUL occurs.

We don't want to do this for possible binaries (like gzip compressed
sitemaps, for example).

See: https://github.com/scrapy/scrapy/issues/2481

## Pipelines
Finally, there are a number of pipeline classes which do various
interesting things:

### CheckContent
Ensures that body text has been extracted for each page, otherwise
raising a logger.error so it is flagged in ScrapingHub

### WordCount
Counts and records words in bodytext.

### NamedPeople
Carries out Named Entity Recognition to identify people mentioned in
news stories.

Note that this pipeline class plays badly with
ScrapingHub (as it requires megabytes of NLTK data which needs to be
fetched from the web or synced with S3 on each run, in the absence
of true persistent storage).

### ReadingAge
Calculates the Flesch reading ease and Flesch-Kincaid grade level for
article bodies. Valid only in English, partly as the tests don't
transfer to other languages well, and partly because we rely on the
CMU pronounciation dictionary for syllable counting, which is only
available in en-US.

Note that this pipeline class plays badly with
ScrapingHub (as it requires megabytes of NLTK data which needs to be
fetched from the web or synced with S3 on each run, in the absence
of true persistent storage).

### Sentiment
Uses textblob to determine and record sentiment and
subjectivity scores for the bodytext of each item.

### StripRawPage
RISJbot is configured to store a Base64-encoded gzipped version of the
raw Response in its JSON output by default. This pipeline class removes
it when needed (for various reasons). It is now enabled by default in
`settings.py`, so if you want the raw Response saved then you will need to set
`STRIPRAWPAGE_ENABLED` to False.
