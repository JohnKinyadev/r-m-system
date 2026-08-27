# Render Deployment

This project deploys the backend API and PostgreSQL database on Render.
The GitHub Pages frontend calls the Render API.

## Expected URLs

- Frontend: `https://johnkinyadev.github.io/r-m-system/`
- Backend API: `https://r-m-system-api.onrender.com`
- Backend health check: `https://r-m-system-api.onrender.com/api/health-check`

## Render Setup

1. Open Render Dashboard.
2. Choose `New` > `Blueprint`.
3. Select the `JohnKinyadev/r-m-system` repository.
4. Select branch `main`.
5. Render will read `render.yaml` and create:
   - `r-m-system-api` Python web service
   - `r-m-system-db` PostgreSQL database
6. Click `Apply`.

The API start command runs `alembic upgrade head` before launching Uvicorn. This keeps migrations working on Render's free web service plan.

## GitHub Pages API URL

The frontend build defaults to:

```text
VITE_API_BASE_URL=https://r-m-system-api.onrender.com
```

If Render gives the backend a different URL, set this GitHub repository variable:

```text
VITE_API_BASE_URL=https://your-actual-render-api-url
```

Then rerun the `Deploy Frontend To GitHub Pages` workflow.

## Notes

Free Render web services can sleep after inactivity, so the first request can be slow.
Free Render Postgres databases expire after 30 days. Upgrade the database before then if you want to keep data long-term.

## Dashboard Troubleshooting

If the Render Dashboard shows `api.render.com/graphql` errors, that error is from Render's dashboard, not this app. Refresh the page, try an incognito window, or temporarily disable VPN/proxy/ad-blocking extensions.

If Blueprint creation still fails, create the services manually with these values:

- PostgreSQL database name: `r-m-system-db`
- Web service root directory: `backend`
- Build command: `pip install --upgrade pip && pip install --default-timeout=180 --retries 10 -r requirements.txt`
- Start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/api/health-check`
- Environment variable `DATABASE_URL`: use the internal connection string from the Render Postgres database
- Environment variable `SECRET_KEY`: generate a long random value
- Environment variable `ALGORITHM`: `HS256`
- Environment variable `ACCESS_TOKEN_EXPIRE_MINUTES`: `10080`
- Environment variable `BACKEND_CORS_ORIGINS`: `https://johnkinyadev.github.io,http://localhost:5176,http://127.0.0.1:5176`
