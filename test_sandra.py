import asyncio
from client.session import Session

async def main():
    s = Session(key_file="sandra_final.pem")
    s.login("sandra", "password123")
    await s.connect()
    Session(key_file="sandra_final.pem")
    s.on_message(lambda sender, text: print(f"\n[FROM {sender}]: {text}"))
    asyncio.create_task(s.listen())

    print("Logged in as Sandra. Ready to receive!")
    while True:
        msg = await asyncio.get_event_loop().run_in_executor(None, input, "Enter message for Ziad: ")
        await s.send("ziad", msg)

asyncio.run(main())