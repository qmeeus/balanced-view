# Twitter Trolls Unveiled

This is a project for the class Knowledge and the Web of the Master in Artificial Intelligence of KU Leuven. The app is available [here](https://fact-checker.herokuapp.com/).

## Requirements
- docker (yup that's it !)

## Installation and running
**NB: Tested on Linux, should be similar on all UNIX-like systems. For Windows 
you probably need to replace `$(id -u)` 
with any number >= 1000. Also, if like me you're using fish shell you probably want to remove the $ sign in front of the variables**<br/><br/>
First build the container. From the project root, run this:<br/>
`docker build -t python3-flask -f Dockerfile.dev --build-arg user_id=$(id -u) .`

Launch the container in deamon mode: <br/>
`docker run -d --name fact-checker -p 5000:5000 -v $(pwd):/home/patrick/src python3-flask`

Navigate to [http://localhost:5000](http://localhost:5000)

Check the logs:<br/>
`docker logs -f fact-checker`

## Debugging
Execute a shell inside the container:<br/>
`docker exec -it fact-checker bash`

## Notes for developers
**Please note that this project is under the GNU General Public License, which authorises you to do pretty much anything with the code except changing the license. In other words, feel free to clone it, transform it or improve it as much as you want, but you can't make it private: it has to remain open source.**

The repository is organised as follow:
 - `/` all the files that have to do with deploying the website, including docker configuration files and various scripts to launch and deploy the app
 - `/app` the code of the website
 - `/app/index.py` the website logic which formulates the logic behind user interactions
 - `/app/api` the code to summarise text and query the news api + the data used for the sources
 - `/app/templates` the various templates of the static webpages
 - `/app/static` static files including css and js libraries used in the webpages

