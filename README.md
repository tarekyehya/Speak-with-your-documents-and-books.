# mini-rag-app

this is minimal implementation of the RAG model for question answering to be in production.

## requirements

- python 3.8 or later

### Install Python using Anaconda

1) Download and install Anaconda from [here](https://docs.anaconda.com/free/anaconda/install/index.html)
2) Create a new environment using the following command:
```bash
$ conda create -n mini-rag-app python=3.8
```
3) activate the environment:
```bash
$ conda activate mini-rag-app 
```
## (Optional) Setup you command line interface for better readability

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```

### setup the environment 

```bash
$ cp .env.example .env
```

Set your environment in the `.env` file. Like `OPEN_API_KEY` value.

## Run the FastAPI server
```bash
uvicorn main:app --reload
```
