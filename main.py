import dotenv
import uvicorn

if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    uvicorn.run(
        "api.app:create_app", host="0.0.0.0", port=8000, factory=True, reload=True
    )
