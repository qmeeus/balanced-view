# BalancedView

The app is deployed [here](http://cardia.cs.kuleuven.be:8080).

Active developer: [Quentin Meeus](https://github.com/qmeeus)

Initiators: [Quentin Meeus](https://github.com/qmeeus) & [Calum Thornhill](https://github.com/cjthornhill) 

This tool started as a project for the course Knowledge and the Web of the Master in Artificial Intelligence of KU Leuven. It is now part of the DIAMOND (Diversity and Information Media: New Tools for a Multifaceted Public Debate) workgroup in collaboration with the universities of Leuven, Antwerpen and Brussels. 

This tool aims to inform the public and interested parties (including journalists) about how a specific fact or event has been covered in the media. It is an attempt to educate online users about fake news and misinformation. It is also an easy way to quickly check whether a fact is real or not.

A paper was published in June 2019 under the name "A Digital Nudge to Counter Confirmation Bias". The publication is available [here](https://github.com/qmeeus/balanced-view/blob/master/documents/Digital_Nudge.pdf).

The authors would like to thank Bettina Berendt and Jeroen Pepperkamp for their help and advices since the early stages of development and for their major role in the writing and proof-reading of the paper.

## Citations
If you find this tool or the publication useful for your research project, please include this citation in your work:

```
@article{10.3389/fdata.2019.00011,
  author    =  {Thornhill, Calum and Meeus, Quentin and Peperkamp, Jeroen and Berendt, Bettina}, 
  title     =  {A Digital Nudge to Counter Confirmation Bias},
  journal   =  {Frontiers in Big Data},
  volume    =  {2},
  pages     =  {11},
  year      =  {2019},
  url       =  {https://www.frontiersin.org/article/10.3389/fdata.2019.00011},
  doi       =  {10.3389/fdata.2019.00011},
  issn      =  {2624-909X},
  abstract  =  {Fake news is an increasing issue on social media platforms. In this work, rather than detect misinformation, we propose the use of nudges to help steer internet users into fact checking the news they read online. We discuss two types of nudging strategies, by presentation and by information. We present the tool BalancedView, a proof-of-concept that shows news stories relevant to a tweet. The method presents the user with a selection of articles from a range of reputable news sources providing alternative opinions from the whole political spectrum, with these alternative articles identified as matching the original one by a combination of natural language processing and search. The results of an initial user study of BalancedView show that nudging by information may change the behaviour of users towards that of informed news readers.}
}
```

## TODO - Project Plan
 - ~~Decoupling services with Kubernetes and docker-compose~~
   - CI/CD (Continuous integration / continuous deployment)
   - Structure (see schema):
     - ~~User Interface (receive input and display response)~~
     - ~~REST API for BalancedView service (json with input and language -> curated selection of articles)~~
       - ~~create DB and at each call, store input/output status/articles~~
     - ~~Translate API (provided by IBM)~~
     - Journalist Interface (adapted to the specific needs of news reporters)
   - Questions:
     - ~~Hosting? (a.t.m. Heroku with the advantages and disadvantages, possible @KUL? AWS?)~~
        - ~~To KU Leuven using Podman instead of Docker ~~
     - ~~What about domain name?~~
     - ~~How to make the site faster? Is it slow because of Heroku?~~ YES
 - ~~Check dutch parsing (and improve if needed)~~
 - Translate the website and option to switch languages
 - Connect to belgian (nl-fr) news providers
   - RSS Feeds -- preferred medium for media providers
     - Any issues from a legal perspective?
   - ~~Categories of news provider - do the current categories still make sense?~~
   - ~~Which news provider provides a developer API? ~~
     - ~~[GoPress](http://api-staging.gopress.be/): ~~
       - ~~General API (not KUL): XML, No documentation, needs a licenseKey~~
       - ~~academic = free access for articles > 2days old but no API (that I know of) + only browser based (need heavy intergration work) ~~
     - ~~[NexisLexis](https://www.lexisnexis.com/communities/academic/w/wiki/111.url-api-specifications.aspx)~~
       - ~~academic: Not recommended, authenticate twice with KUL account + only browser based (need heavy intergration work)~~
       - ~~General API: authentication & access not clear~~
 - Translation service: IBM vs ~~Google Translate~~ DeepL
   - IBM: not always stable 
   - ~~Google: more expensive & need billing information even for free API calls~~
 - Multilingual support (provide translated articles from other languages)
 - Matching algorithm:
   - ~~Move from TextRank to Deep Learning? (Graph Convolutional Nets, Bi-LSTM?)~~ NOT PRIORITY
     - ~~Is it necessary since with the modifications, the summarisation works fine?~~
   - ~~Latest developments in NLP (Attention is all you need)~~
   - ~~Strategy: training data / unsupervised learning / train and host vs continuous learning~~
 - ~~Connect DB and store searches?~~ Elasticsearch for storage
   - ~~If yes: requirements > GDPR?~~
 - Develop journalist interface (needs input from the concerned parties)

![Building blocks](misc/appview.jpg)

## Notes for developers
**Please note that this project is under the GNU General Public License, which authorises you to do pretty much anything with the code except changing the license. In other words, feel free to clone it, transform it or improve it as much as you want, but you can't make it private: it has to remain open source.**

**I do not guarantee that the information below is up to date (the directory structure certainly isn't)**

The repository is organised as follow:
 - `/` all the files that have to do with deploying the website, including docker configuration files and various scripts to launch and deploy the app
 - `/app` the code of the website
 - `/app/index.py` the website logic which formulates the logic behind user interactions
 - `/app/api` the code to summarise text and query the news api + the data used for the sources
 - `/app/templates` the various templates of the static webpages
 - `/app/static` static files including css and js libraries used in the webpages

## Requirements
- a computer (preferably running linux) with an internet connection and either docker or podman installed (the rest is automatically included when builing in the containers)
- the docker daemon must be running if docker is the preferred option

## How to build and deploy locally?
There are (currently) 4 services required to run the full app:
    1. web server: nginx
    2. data storage: elasticsearch
    3. the API
    4. the UI
   
The easiest option to start everything is to use the `bootstrap.sh` script. Since `podman` takes more time to build containers than `docker`, I prefer to build the containers manually with docker and push them to the docker hub, using the following syntax:
```bash
docker build -t <image-tag> <context-dir>
docker login
docker push <image-tag>
``` 

The `bootstrap.sh` script will automatically download the containers or build them if the flag `-u` is provided. It will also automatically restart the containers if the flag `-r` is provided.

If the preferred option is to use `docker`, you have to notice that some containers run as root. To fix this security issue, it is advised to modify the `Dockerfile` to run as a user.

**NB**: Tested on Linux, should be similar on all UNIX-like systems equiped with Docker. For Windows 
you probably need to replace `$(id -u)` 
with any number >= 1000. Also, if like me you're using fish shell you probably want to remove the `$` sign in front of the variables<br/><br/>
