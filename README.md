

# Discord Webhook Notifications with AWS Lambda

Using my [AWS Lambda CDK Template](https://github.com/pagorska/lambda-cdk), I'll set up Discord webhooks to post through my lambda. 
Discord webhooks are perfect for hobby projects. They're free, take very little time to set up, and very few requirements compared to sending SMS and email alerts. They're great for alerting for anything related to your projects or any automated alerts. In this example, I'll be scraping availability from [Ross Lake Resort](https://www.rosslakeresort.com/stay), a resort in the North Cascades with a way too difficult process for booking, and sending a Discord message to a dedicated alerting channel when I find availability. You can replace this with any API or website you'd like to scrape.

**Relevant Resources**
* [Discord Developer Docs](https://discord.com/developers/docs/intro)
* [AWS Lambda CDK Template](https://github.com/pagorska/lambda-cdk)
* [AWS CDK Docs](https://docs.aws.amazon.com/cdk/v2/guide/home.html)
* [PyPi DiscordWebhook](https://pypi.org/project/discord-webhook/)



## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [1. Set Up Discord Webhook](#1-set-up-discord-webhook)
  - [2. Configure Environment Variables](#2-configure-environment-variables)
  - [3. Add Data](#3-add-data)
  - [4. Post with Webhook](#4-post-with-webhook)
  - [5. Deploy with CDK](#5-deploy-with-cdk)
- [Summary Basic Example](#summary-basic-example)


## Prerequisites 

- AWS Account
- [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) installed
- Discord Account & Server (I recommend creating a dedicated alerts server)
- Python 3.9+ 

## Setup Instructions

### 1. Set Up Discord Webhook

Create a webhook in your Discord server to receive availability alerts. You must have mod level or higher permissions in this server, and I recommend creating a server specifically for alerting and logs from lambdas. 

**Note:** This must be done on Discord's desktop app or website (not mobile).

1. Navigate to your desired channel (or create `#availability-alerts`)
2. Hover over the channel → ⚙️ **Edit Channel**
3. Go to **Integrations** tab -> Webhooks
4. Click **Create Webhook**
5. Name your webhook 
6. **Copy the webhook URL** - you'll need this next

![Setup Example](https://github-readmes.s3.us-east-1.amazonaws.com/discord-example/webhook%20create.png)

### 2. Configure Environment Variables

Your webhook URL must be kept secure since it allows posting to your Discord channel. I would not recommend posting this publicly to your github repo. Keep the URL in a .env when working locally, and within your Github repository's secrets if deploying via Github Actions, or use your preferred secrets manager.

**For Local Development:**
Create a `.env` file in your lambda folder:
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-url-here
```
Ensure `.env` is in your `.gitignore`.

**For Deployments via Github Actions:**
1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `DISCORD_WEBHOOK_URL`
4. Value: Your webhook URL

![Github Repository Secrets](https://github-readmes.s3.us-east-1.amazonaws.com/discord-example/webhook%20url.png)

### 3. Add Data 

You're able to post any text to the webhook. If you'd like to just test webhook functionality for now, skip this step and post anything to the Webhook. If you're pulling data from a particular API, I'd recommend adding a testing step to confirm if it works when calling from AWS as well as locally.

I use `requests` and `BeautifulSoup` to pull the information from the table on the site, and because I don't know what it looks like if there's actually availability, I also will post a message if I can't find the components I was using for availability checking before, and if the word 'unavailable' shows up more or less than 4 times.

![Ross Lake Table](https://github-readmes.s3.us-east-1.amazonaws.com/discord-example/ross%20lake%20table.png)

```python
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
```

### 4. Post with Webhook

Once you have some message to post to your channel, create a `DiscordWebhook` object with your previously saved URL, add a message title and description (be sure to format it with new lines and such for cleanliness), add the embed to the webhook, and execute. At this point, if you're testing locally or executing your lambda, a message will fire.

```python
from dotenv import load_dotenv
from discord_webhook import DiscordWebhook, DiscordEmbed
load_dotenv()  

discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
webhook = DiscordWebhook(url=discord_webhook_url)

embed = DiscordEmbed(
    title="Possible Cabin Availability",
    description=messageBody)

webhook.add_embed(embed)
webhook.execute()
```
I configure the messages to only send if there is some of the availability I'm seeking, but for this example, I posted a few messages to test:

![Messages](https://github-readmes.s3.us-east-1.amazonaws.com/discord-example/example%20message.png)

### 5. Deploy with CDK

**Before deploying,** confirm the interval you'll be running your lambda on, and be mindful of not overloading the site or API you're using. If a site only updates every hour, there's no reason to scrape every 2 minutes, as it is wasteful for both parties. In my example, I'm running the scrape lambda every 30 minutes. If I discover that availability is only ever posted, for example, on weekday mornings, then I'd adjust my schedule to only run within that timeframe on a shorter schedule.

Deploy to AWS Lambda using your CDK template:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate.bat
pip install -r requirements.txt

cdk bootstrap # once per account/region

cdk synth
cdk deploy
```
Or, push to main with a commit message beginning with **deploy:** [if you've set up OIDC](https://github.com/pagorska/lambda-cdk?tab=readme-ov-file#github-actions-setup-optional). If you're deploying multiple different projects with CDK, make sure to use different stack names. 

## Summary Basic Example

Add `discord-webhook` to your `requirements.txt` or `pip install discord-webhook`.

```python
from discord_webhook import DiscordWebhook

webhook = DiscordWebhook(url="your-webhook-url")
webhook.content = "Simple text message"
webhook.execute()

embed = DiscordEmbed(
    title="title",
    description="body")

webhook.add_embed(embed)
webhook.execute()
```
