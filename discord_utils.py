def send_messages_to_discord(client, secret, message_list):
    TOKEN = secret["discord_exemple"]["token"]

    @client.event
    async def on_ready():
        channel_id = int(secret["discord_exemple"]["channel"])
        channel = client.get_channel(channel_id)

        for message in message_list:
            await channel.send(message)

        await client.close()

    client.run(TOKEN)
