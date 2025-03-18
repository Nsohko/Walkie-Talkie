# WALKIE - TALKIE
## By Ready.Set.Go Tech

Welcome to the Walkie - Talkie: A tool aimed at educating, engaging and empowering our elderly while
complementing our healthcare services.

Walkie-Talkie is an AI-driven chatbot designed to assist elderly users with daily engagement, cognitive stimulation, and health-related support. By integrating conversational AI with healthcare guidance, 
the chatbot enhances the well-being of seniors while reducing the burden on caregivers and medical professionals.
The chatbot also conducts sentiment analysis on user interactions based on the National Healthcare Group's 3E5P framework to provide healthcare practioners with information on patients' state of change. This enables more targetted and effective healthcare outcomes in the long run.

The chatbot utilises Retreival-Augmented-Generation (RAG) to search through provided MOH documents and provide users with accurate and up-to-date information.
This is powered through the Intersystem's IRIS database, which allow for efficient storage and similarity lookup of these documents once vectorised

Please see the video below for further information:

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/Gzx_ZwWr_OU/0.jpg)](https://www.youtube.com/watch?v=Gzx_ZwWr_OU)

## Setup Instructions
Clone this repo via ...

cd into the directory

Note: You will need an OpenAI API key with credits to use this app.

### 1. Quick Set Up Via Docker
Please ensure that Docker is installed.
Then enter the following commands

```
docker build -t walkie-talkie .
docker run -e OPENAI_API_KEY="YOUR-OPENAI-API-KEY-HERE" -p 5000:5000 walkie-talkie
```
Please replace the "YOUR-OPENAI-API-KEY-HERE" in the above command with your actual openAI API key.
The service should be accessible at [https://localhost:5000](https://localhost:5000)

### Developer Setup via Anaconda
Ensure that conda, node.js and yarn are installed.

Create a new conda env, and activate it:
```
conda create --name myenv python=3.10
```

In the project rppt, create .env file with your openAI API Key.
```commandline
OPENAI_API_KEY=YOUR-KEY-HERE
```

#### Starting IRIS database
Install IRIS Community Edtion in a container. This will be your SQL database server. More information can be found [here](https://github.com/intersystems-community/hackathon-2024/tree/main)
```
docker run -d --name iris-comm -p 1972:1972 -p 52773:52773 -e IRIS_PASSWORD=demo -e IRIS_USERNAME=demo intersystemsdc/iris-community:latest
```

#### Starting backend
From the project root, enter the following commands:
```
cd backend
pip install -r requirements.txt
pip install ./install/intersystems_irispython-5.0.1-8026-cp38.cp39.cp310.cp311.cp312-cp38.cp39.cp310.cp311.cp312-win_amd64.whl
flask run
```
This will start up the backend. Note: The above is assuming this is being run on windows. For information on other Operating System, please see [here](https://github.com/intersystems-community/hackathon-2024/tree/main)

#### Starting the frontend
From the project root, enter the following commands
```
cd frontend
yarn install
yarn start
```
This will start the frontend

The service will now be available at [https://localhost:3000](https://localhost:3000)


