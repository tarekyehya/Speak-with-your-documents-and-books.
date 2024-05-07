from fastapi import FastAPI
app = FastAPI()



@app.get("/welcome")
def welcome():
    return {
        "message":"Hello World",
        "user_name":"Tarek Yahia"
    }


# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)


