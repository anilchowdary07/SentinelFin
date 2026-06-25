import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn

app = FastAPI()

async def my_gen():
    try:
        for i in range(10):
            print(f"yielding {i}")
            yield f"data: {i}\n\n"
            await asyncio.sleep(1)
    except Exception as e:
        print(f"CAUGHT EXCEPTION IN GEN: {repr(e)}")

@app.get("/stream")
def stream():
    return StreamingResponse(my_gen(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)
