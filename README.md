# Twitter Trolls Unveiled

This is a project for the class Knowledge and the Web of the Master in Artificial Intelligence of KU Leuven. The app is available [here](https://fact-checker.herokuapp.com/).

## Requirements
- docker (yup that's it !)

## Installation and running
**NB: Tested on Linux, should be similar on UNIX-like systems. For Windows 
you probably need to replace `$(id -u)` 
with any number >= 1000.**<br/><br/>
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
