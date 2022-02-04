from uvicorn import run

from app import app

if __name__ == '__main__':
    run(app=str(app), host="127.0.0.1", reload=True)
