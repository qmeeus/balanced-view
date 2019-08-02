# BalancedView

This was originally a project for the class Knowledge and the Web of the Master in Artificial Intelligence of KU Leuven. It is developed as a tool to provide information about media coverage of some specific events / facts. The app is available [here](https://fact-checker.herokuapp.com/). The publication is available [here](https://github.com/qmeeus/balanced-view/blob/master/documents/Digital_Nudge.pdf)

Authors: [Quentin Meeus](https://github.com/qmeeus) & [Calum Thornhill](https://github.com/cjthornhill) under the supervision of [Bettina Berendt](https://people.cs.kuleuven.be/~bettina.berendt/) and [Jeroen Pepperkamp](https://www.kuleuven.be/wieiswie/en/person/00117249)

Active developer: [Quentin Meeus](https://github.com/qmeeus)

![Building blocks](images/appview.jpg)

## Requirements
- docker (yup that's it !)

## How to build and deploy locally (for developers)?
1. First build the container. From the project root, run this:<br/>
`docker build -t python3-flask -f Dockerfile.dev --build-arg user_id=$(id -u) .`

2. Launch the container in deamon mode: <br/>
`docker run -d --name fact-checker -p 5000:5000 -v $(pwd):/home/patrick/src python3-flask`

3. Navigate to [http://localhost:5000](http://localhost:5000)

4. Check the logs:<br/>
`docker logs -f fact-checker`

5. Command-line debugging of the container: <br/>
`docker exec -it fact-checker bash`


**NB**: Tested on Linux, should be similar on all UNIX-like systems equiped with Docker. For Windows 
you probably need to replace `$(id -u)` 
with any number >= 1000. Also, if like me you're using fish shell you probably want to remove the $ sign in front of the variables<br/><br/>

## Notes for developers
**Please note that this project is under the GNU General Public License, which authorises you to do pretty much anything with the code except changing the license. In other words, feel free to clone it, transform it or improve it as much as you want, but you can't make it private: it has to remain open source.**

The repository is organised as follow:
 - `/` all the files that have to do with deploying the website, including docker configuration files and various scripts to launch and deploy the app
 - `/app` the code of the website
 - `/app/index.py` the website logic which formulates the logic behind user interactions
 - `/app/api` the code to summarise text and query the news api + the data used for the sources
 - `/app/templates` the various templates of the static webpages
 - `/app/static` static files including css and js libraries used in the webpages

## TODO - Project Plan
 - CI/CD (Continuous integration / continuous development)
 - Decoupling services with Kubernetes and docker-compose
   - Structure:
     - User Interface (receive input and display response)
     - REST API for BalancedView service (json with input and language -> curated selection of articles)
     - Translate API (provided by IBM)
     - Journalist Interface (adapted to the specific needs of news reporters)
   - Questions:
     - Hosting? (a.t.m. Heroku with the advantages and disadvantages, possible @KUL? AWS?)
     - What about domain name?
 - Check dutch parsing (and improve if needed)
 - Translate the website and option to switch languages
 - Connect to belgian (nl-fr) news providers (legal requirements regarding scraping)
    - Which news provider provides a developer API?
    - Are there fees to pay?
    - What can we scrape without risk of infringing IP laws?
 - IBM Translation service
 - Multilingual support (provide translated articles from other languages)
 - Matching algorithm:
   - Latest developments in NLP (Attention is all you need)
   - Strategy: training data / unsupervised learning / train and host vs continuous learning
 - Connect DB and store searches?
   - If yes: requirements > GDPR?
 - Develop journalist interface (needs input from the concerned parties)

