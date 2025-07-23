import requests
import json
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook, DiscordEmbed

def lambda_handler(event, context):
    load_dotenv()  
    discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    webhook = DiscordWebhook(url=discord_webhook_url)

    try:
        messageBody = ''
        url = 'https://www.rosslakeresort.com/stay'

        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        cabin_names = [
            'Little Cabin',
            'Modern Cabin ',
            'Bunkhouse Cabin',
            'Peak Cabin'
        ]
        
        availability_containers = [
            'comp-ku31x181',  # Little Cabin availability
            'comp-lyyw3epq',  # Modern Cabin availability
            'comp-lk34hktn',  # Bunkhouse Cabin availability
            'comp-lmguuf9t'   # Peak Cabin availability
        ]

        for i, container_id in enumerate(availability_containers):
            container = soup.find('div', id=container_id)
            if container:
                status_text = container.get_text(strip=True)
                if status_text.lower() != 'unavailable':
                    messageBody += f"{cabin_names[i]}: {status_text}\n"
            else:
                messageBody += f"{cabin_names[i]}: Not found. Webpage structure may have changed\n"

        # Sanity check - has the number of times 'Unavailable' been found changed?
        body = soup.find('body')
        if body:
            body_text = body.get_text()
            word_count = body_text.lower().count('unavailable')
            if word_count != 4:
                messageBody += f"Unknown availability: Expected 4 'Unavailable' mentions, found {word_count}.\n"
    
    
        if messageBody:
            messageBody = f"Available cabins:\n{messageBody}"
            messageBody += "\nhttps://www.rosslakeresort.com/stay"
            messageBody += "\nhttps://www.rosslakeresort.com/contact"
            embed = DiscordEmbed(
                title="Possible Cabin Availability",
                description=messageBody)
            webhook.add_embed(embed)
            webhook.execute()
        else:
            messageBody = "No cabins available at the moment."
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': messageBody,
            }),
        }
    except Exception as e:
        messageBody = f"Error fetching data: {str(e)}"
        embed = DiscordEmbed(
            title="Error",
            description=messageBody)
        webhook.add_embed(embed)
        webhook.execute()
        return {
            'statusCode': 500,
            'body': messageBody,
        }