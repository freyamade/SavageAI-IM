# SavageAI/IM

An exploration into LangChain and making a little AI Bot to ask questions to in Discord.

Not really designed to be something heavily used by people, it's more just a learning experience for me, but the repo is public and you can deploy your own instance if you wish!

I'd host one publicly if people wanted it but as LLMs cost money, it would have to be a premium system.
If you would like this, please open an issue or let me know in the SavageAim discord!

# Usage
Bot is deployable using Docker, or `poetry` if you want to run it without docker.

```bash
poetry run python3 -m savage_ai_im
```

SavageAI-IM is by default powered by Google Vertex AI, which is the first one I managed to get working.
I can try and make the backend configurable in future if people want it.

## Setup
There are some required environment variables that need to be present either in the Docker container or in the shell that calls the above `poetry` command;

- `DISCORD_TOKEN`: The Discord Bot Token for your application. If you do not have one, you need to create a Bot on the Discord Developer Console.
- `GOOGLE_APPLICATION_CREDENTIALS`: A path to a file that contains the credentials for a Google Cloud Platform Service Account that has access to the Vertex AI API.

There are also some optional env vars that can be set;

- `SENTRY_DSN`: If you have a sentry.io account, you can add a DSN for one of your projects so that the bot can report errors to it.

- `LANGCHAIN_TRACING_V2`
- `LANGCHAIN_ENDPOINT`
- `LANGCHAIN_API_KEY`
- `LANGCHAIN_PROJECT`
  - The above can be set if you want to set up langchain tracing to see how your traces are going.

## Docker Compose
The `docker-compose.yml` file is set up to run the image pretty straightforwardly, you just need to do the following;

1. Download the Service Account Credentials JSON into a file named `gcp-creds.json` that is in the same directory as the docker-compose file
2. Populate the DISCORD_TOKEN environment variable with your created Bot Account token
3. Populate the other optional variables as needed
4. Run `docker compose up` and it should work :D
