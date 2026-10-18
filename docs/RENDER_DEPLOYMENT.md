# Deploy the demonstration on Render

**Hosted demonstration:** https://aegis-rebound.onrender.com/

The dashboard needs a Python **Web Service** because its replay and inference API runs on the server. The frontend and API are served together; a separate static-site deployment is unnecessary.

## Dashboard setup

1. Sign in at https://dashboard.render.com and choose **New > Web Service**.
2. Connect your GitHub account and select `B-Sheikh/Aegis-REBOUND`.
3. Select branch `main`, language **Python 3**, and leave **Root Directory** blank.
4. Enter **Build Command**: `pip install -r requirements.txt`.
5. Enter **Start Command**: `python app.py --host 0.0.0.0 --port $PORT --no-browser`.
6. Select the **Free** instance for a demonstration. Set **Health Check Path** to `/api/patients` under Advanced, then create the web service.

No secrets, database, disk, or API keys are required. The included `.python-version` selects Python 3.13 with Render's latest available patch. The included `render.yaml` defines the equivalent setup for Render's Blueprint flow.

When the deployment shows **Live**, open the HTTPS `onrender.com` URL shown on your service page. The actual hostname depends on availability; use Render's displayed URL. Verify the initial case, optional measurement update, Sensor gap, and Experiments screens. The hosted demonstration URL is linked near the top of the repository README.

## Free service behavior

Render's free web services spin down after 15 minutes without inbound traffic. The next visit can take about a minute to wake the service. Open and test the link before a live demonstration. Current service limits: https://render.com/docs/free .

## Troubleshooting

- **No open port detected:** use the exact start command above, including `--host 0.0.0.0` and `$PORT`.
- **app.py or requirements.txt missing:** leave Root Directory blank; these files are at the repository root.
- **Unknown --host argument:** deploy the latest `main` commit.
- **Build fails:** inspect Render's build logs. Confirm the Python runtime and dependency installation command.

This hosted service demonstrates the included synthetic cases and the same research model as the local application.

Official setup reference: https://render.com/docs/web-services .
