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
