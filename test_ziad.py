import asyncio
from client.session import Session

async def main():
    s = Session(key_file="ziad_final.pem")
    s.login("ziad", "password123")
    await s.connect()
    s.on_message(lambda sender, text: print(f"\n[FROM {sender}]: {text}"))
    asyncio.create_task(s.listen())
    print("Logged in as Ziad. Ready to receive!")
    while True:
        msg = await asyncio.get_event_loop().run_in_executor(None, input, "Enter message for Sandra: ")
        await s.send("sandra", msg)

asyncio.run(main())