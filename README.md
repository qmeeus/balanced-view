# Twitter Trolls Unveiled

This is a project for the class Knowledge and the Web of the Master in Artificial Intelligence of KU Leuven.

## Data
Twitter published [here](https://about.twitter.com/en_us/values/elections-integrity.html#data) a dataset of tweets reportedly published by trolls. It includes information from 3,841 accounts believed to be connected to the Russian Internet Research Agency, and 770 accounts believed to originate in Iran.

## Planning
- Exploratory analysis
- Research Question

## What is where?
- [english.csv](https://drive.google.com/open?id=1163S0jWSjCsX-fEpVY3nv8KrVpzkdYb5)
- [overleaf report](https://www.overleaf.com/5771853674fkgchqmfmhqp)
- [stack channel](https://mai-1819.slack.com/messages/GDH4FFL69)
- [data](https://about.twitter.com/en_us/values/elections-integrity.html#data)

## Requirements
- docker
- python >=3.5

## Installation and running
**NB: Tested on Linux, should be similar on UNIX-like systems. For Windows 
you probably need to replace `$(id -u)` 
with any number >= 1000.**<br/><br/>
First build the container. From the project root, run this:<br/>
`docker build -t ubuntu-flask --build-arg user_id=$(id -u) .`

Launch the container in deamon mode: <br/>
`docker run -d --name twitter -p 5000:5000 -v $(pwd):/home/patrick/src ubuntu-flask`

Navigate to [http://localhost:5000](http://localhost:5000)

Check the logs:<br/>
`docker logs -f twitter`

## Training
Launch bash inside the container:<br/>
`docker run -it --name twitter -v (pwd):/home/patrick/src ubuntu-flask bash`

Go to the right folder: <br/>
`cd model`

Train and save the model:<br/>
`python keyword_detection.py --save`
