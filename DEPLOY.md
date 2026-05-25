# Deployment Guide

This guide provides instructions on how to deploy the MultiExchange-HFT MVP dashboard to Streamlit Community Cloud.

## Streamlit Community Cloud (Recommended for Dashboard)

Streamlit Community Cloud is the easiest way to deploy the Streamlit dashboard for free.

### Steps to Deploy:

1. **Push your code to GitHub:**
   Ensure your repository is up to date on GitHub. The repository must be public (or you must grant Streamlit access to your private repos).

2. **Sign up / Log in to Streamlit Community Cloud:**
   Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.

3. **Deploy a new app:**
   - Click the "New app" button.
   - Select your GitHub repository from the dropdown menu.
   - Set the **Branch** to your working branch (e.g., `main` or `feat/mvp-implementation`).
   - Set the **Main file path** to `app.py`.

4. **Configure Secrets / Environment Variables:**
   Before clicking "Deploy", click on **"Advanced settings..."**. You need to configure the required environment variables in the TOML format provided by Streamlit secrets.

   Add the following variables:
   ```toml
   PAPER_MODE = "true"
   DB_PATH = "data/trades.db"
   ```

5. **Deploy:**
   Click **"Deploy!"**. Streamlit will automatically read the `requirements.txt` file, install dependencies, and launch your application.

## Required Environment Variables

Regardless of the deployment platform, the following environment variables are supported/required:

- `PAPER_MODE`: Set to `true` to execute paper trades securely without connecting to live brokerages.
- `DB_PATH`: Set the path to the database file (e.g. `data/trades.db`). Ensure the hosting platform allows file persistence in this directory, or use an external database path if deploying as a scalable container.
