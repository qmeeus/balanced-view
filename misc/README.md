
# BalancedView

## Introduction

BalancedView was initiated by Quentin Meeus and Calum Thornhill in the fall of 2018. Fake news was a hot topic and spread faster and further on the web than cholera in a glass of water. Of course, the manipulation of information is not something new and is mastered by dictatorial regimes and shady political persons for ages. What makes it more of a problem now than at any other time in History then? Well in this Internet age, the amount of information that each of us is exposed to each day is staggering, whether it comes from news media, blogs, forums, Facebook, Instagram or Google. Anyone can share anything without control whatsoever. Obviously, this has advantages in terms of freedom of speech, but it also means that it is much more complicated to verify each piece of information.

Some social networks and NGO's started to look into the problem, trying to detect false information as it is published or shared. Generally, the approach taken requires experts and journalists to fact check each piece of information manually and flag news articles as "fake" by the means of a sticker. In the literature, this is what is called a nudge by information. The idea is to control the spreading of incorrect information by letting the user know that a given article probably contains dubious or incorrect statements. The approach chosen in BalancedView is more of an educational one, where the user is encouraged to research and assess by himself the quality of articles found online. This is referred to as a nudge by presentation. This choice is motivated by the so-called "confirmation bias" effect, according to which one accepts more easily arguments aligned with one's beliefs rather than arguments that contradicts them. Further, we think that it is imperative that people start to question everything that is read online and learn how not to fall into passively absorbing information without verifying its validity.

> "It ain't what you don't know that gets you into trouble. It's what you know for sure that just ain't so."
> Mark Twain

For more information about nudges, confirmation bias and the other vicious effects that all contributes to the spread of misinformation online, please refer to [our paper](documents/Digital_Nudge.pdf). The remaining of this document is divided into 3 sections: first a brief overview of the tool, including a word about the design choices, the technical specifications of the tool as well as the motivation behind technical choices and finally a section about future developments, with the learnings and recommendations obtained through a user test.

## Overview

Instead of using machine learning to identify incorrect statements and flag them as fake, the chosen approach is educational. The motivation is to give users the tools to verify themselves information found online.

> "Give a man a fish, and you feed him for a day. Teach a man to fish, and you feed him for a lifetime."
> Lao Zi

The tool is composed of three major components: the user interface (UI), the application programming interface (API) and a data storage. The role of the latter is pretty self-explanatory.

The user interface is composed of one screen that is designed to be very user-friendly and intuitive. The main purpose is to offer an interface to non-technical users to interact with the program. When a user enters the url, he is greeted with a simple input box where he can enter text, and a submit button. Once a text is submitted, multiple articles coming from popular media providers are displayed under the form and classified in three categories. Originally, the choice was made to use political orientation to divide the articles. Indeed, in the early stages of development, the focus was on the US and UK, where such as separation made sense. The political orientation of each source originated from a research on political bias in the media from the university of <?>. Later on, as the project gain interest from third parties in Belgium, the focus shifted towards Belgian news, and naturally the differences between media reporting across the linguistic border. It seemed interesting as well to include articles in English in a third category for all international articles. By default, only three items are displayed from most relevant to least relevant. Again, the motivation behind this design decision was to keep the layout simple and intuitive, without flooding the user with too much information. The items include the media source, the title of the article, a short summary of the contents, an image, if it is available and the date of publication. The title redirects to the full original article.

The API is where all the complexity happens. It has two main endpoints, or functions: one is to process and analyse text in multiple languages and the second performs queries to retrieve relevant documents stored in the data storage backend. Additionally, it populates the database at regular intervals with the latest news articles. Each endpoint accepts a number of options to perform analysis and search and to organise the results.

At the moment of writing, only the user interface is available publicly ([here](http://cardia.cs.kuleuven.be:8080)) and it should stay that way in the future to keep to a minimum the possibilities to misuse the program.

## Technical Specifications

### Technological stack and architecture

The program relies on a number of software and libraries. First and foremost, the program is designed to work on a Linux system. Although it should work on other operating systems, it has never been tested and expect major issues if you want to make things work with Windows. Next, each component is self-contained in its own environment in the form of an [OCI container](https://www.opencontainers.org/). In particular, the technology used is [`podman`](https://podman.io). Compared to the better known [`docker`](https://www.docker.com), it provides the advantage to run rootless, by mapping the `uid` of the root user in the container to the `uid` of the current user on the host. Although `podman` is pretty new at the time of the writing, it is already well developed and uses the same syntax and options as `docker` (for the most parts). When possible, `podman` should use `overlayfs`  as the underlying file system, rather than the default vfs. Indeed, [as `docker` developers put it](https://docs.docker.com/storage/storagedriver/select-storage-driver):

> The vfs storage driver is intended for testing purposes, and for situations where no copy-on-write filesystem can be used. Performance of this storage driver is poor, and is not generally recommended for production use.

That being said, depending on the version of the Linux kernel, [this is not always possible for older kernels but any kernel version > 4.18.0 should work](https://github.com/containers/fuse-overlayfs).

The data storage backend uses [Elasticsearch](https://www.elastic.co/products/elasticsearch), which is a "distributed, RESTful search and analytics engine capable of addressing a growing number of use cases". It is fast, simple of use and particularly well suited for storing and accessing unstructured data such as text. Its growing adoption in the dev community and the integration of other tools such as `Kibana`, `Filebeat` and `Logstash` makes it particularly relevant for our use case.

Language translation and identification is handled by the [IBM Cloud Language Translator API](https://cloud.ibm.com/catalog/services/language-translator). The main reason behind this choice is the price (it provides access to default models without cost until the threshold of 1.000.000 characters per month is reached and does not require credit card information until reaching this threshold). Other service providers such as `Google Translate` and `DeepL` have been considered but were discarded because of the pricing.

The database is populated at regular intervals with [RSS feeds](https://en.wikipedia.org/wiki/RSS) of configured media sources ([available here](https://github.com/qmeeus/balancedview-api/blob/master/api/data_provider/sources/resources/rss_sources.json)) and the latest news provided by the [NewsAPI](https://newsapi.org). At the time of writing, the database is updated 3 times a day, at 6:00 AM, 12:00 PM and 6:00 PM using a [cronjobs](https://en.wikipedia.org/wiki/Cron).

Both the API and the UI are developed using [Python](https://www.python.org) and [Flask web application framework](https://palletsprojects.com/p/flask). Both are easy to learn and allow for fast developments. Additionally, the API uses the [elasticsearch-dsl](https://elasticsearch-dsl.readthedocs.io/en/latest/) to communicate with Elasticsearch backend and [spacy](https://spacy.io/) to perform NLP tasks.

Finally, we use [`gunicorn`]() as web server gateway interface (WSGI) rather than the default `flask` server, which is not suited for production, and [Nginx](https://www.nginx.com/) as webserver. It is an open source software which can also be used as a reverse proxy load balancer. It takes care of dispatching the incoming connections as well as some key security aspects.

### User and developer documentation

The UI is pretty intuitive for anyone with some experience with developing flask website and we will thus not develop it here. For a general understanding, it suffices to say that the only thing that it does is to capture user input, format it in a JSON document to forward to the API and display the API results in a web page.

The API relies on more complex components and deserves a more exhaustive explanation. As mentioned earlier, it currently has two endpoints, one to find relevant articles and one to analyse texts. Each endpoint accepts a number of options that should be provided as a JSON document. Default options that apply to both endpoints include:

- `output_language`: the language in which the results should be returned (not implemented);
- `search_languages`: a list of relevant languages to search the database;
- `groupby_options`: a set of options to organise the results in groups:
  - `key`: a string that correspond to the name of the field in the database to group the data;
  - `default`: a string that correspond to the name of the default group;
  - `orderby`: a string that correspond to the name of the field used to sort the results;
  - `reverse`: a boolean field that decides whether the results should be sorted in reverse order;
  - `max_results_per_group`: an integer to limit the number of results;
  - `groups`: a list of groups, composed of a name for the group and a value to match each result.

The first endpoint is available at \<api-url\>/articles and has the following options:
- `terms`: a list of strings that corresponds to the query terms to be matched against the database;
- `source_language`: a string corresponding to the language ISO code of the terms.

When a request comes in through this endpoint, the terms are translated in each of the requested search languages and a number of queries are built, one for each language, to match against document in the database. An example query is showed below (see [Elasticsearch Query DSL documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-filter-context.html) for background on what this means):

```json
{
  "query": {
    "bool": {
      "must": [{"match": {"language": "nl"}}],
      "minimum_should_match": 2,
      "should": [
        {"multi_match": {"fields": ["body", "title"], "type": "phrase", "query": "Midi"}},
        {"multi_match": {"fields": ["body", "title"], "type": "phrase", "query": "Noord"}},
        {"multi_match": {"fields": ["body", "title"], "type": "phrase", "query": "kruising"}},
        {"multi_match": {"fields": ["body", "title"], "type": "phrase", "query": "werken"}},
        {"multi_match": {"fields": ["body", "title"], "type": "phrase", "query": "storingen"}}
      ]
    }
  }
}
```

The `minimum_should_match` argument is calculated according to this rule: `minimum_should_match = int(0.5 * len(terms))`. If matching documents are found, they are formatted according to the `groupby` options, if provided, and returned to the client. Otherwise, an error message is returned.

The second endpoint is available at \<api-url\>/analysis and has the following options:

- `input_text`: a string, the text on which the analysis should be performed;
- `related`: a boolean field that decides whether to include output from the article endpoint or not.

When a requests comes in, the input text is cleaned (at the moment, the only operation is to redundant spaces) and a hash is calculated on it. We try to match the hash to an existing document id in the database. If it is found, the document is retrieved with the analysis results. This allows to prevent the same expensive operations to be recalculated multiple time and save precious CPU time. If the document was not seen before, we use IBM Language Translator to identify the language and load the corresponding `spacy` model. We filter stop words, extract tokens, part-of-speech tags and named entities from the text and pass them to `TextRank` algorithm which builds a graph that models token co-occurences. The `TextRank` score is calculated based on the centrality of each token in the text. The measure of centrality denotes of how many nodes a node points to and how many nodes points to it. If necessary, we get related articles using the identified language and the top keywords found by `TextRank` as query terms for the `articles` endpoint.

*A note on efficiency:* `Spacy` models can be relatively expensive to load. For this reason, if they were loaded at each request, the website would be very slow, causing timeout errors most of the time. For this reason, the decision was made to load the models when the container starts and store them in a dictionary. This has a considerable impact on memory but relieves a great deal of the pressure on the CPU. Nonetheless, this limits possibilities for adding new languages because that means that each new model have to be stored in memory. For example, if `gunicorn` is using 3 workers and there are 3 language models, 9 models in total are loaded at boot.  

## Future developments
