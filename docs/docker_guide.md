# Docker Deployment Guide 🐳

This guide provides instructions and resource recommendations for running the Browser-Testing Suite using Docker.

## System Requirements
- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux).
- **RAM**: Minimum 4GB (8GB recommended for multiple concurrent browser tasks).
- **Disk Space**: ~2GB for images and dependencies.

## Resource Allocation (Calculated)

To ensure stability during browser automation, the following limits are applied in `docker-compose.yml`:

| Service | Memory Limit | CPU Limit | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend** | 4.0 GB | 1.0 CPU | Running FastAPI + Chromium (Playwright) |
| **Frontend** | 1.0 GB | 1.0 CPU | Next.js Server Side Rendering |
| **MLflow** | 1.0 GB | 1.0 CPU | Tracking UI and Data Logging |

> [!IMPORTANT]
> The Backend service requires significant memory when launching Chromium. If you encounter "Out of Memory" errors, consider increasing the memory limit to 4GB.

## Getting Started

1. **Environment Setup**:
   Ensure you have a `.env` file in the root directory with your API keys (Google, OpenAI, etc.).

2. **Launch Services**:
   ```powershell
   docker compose up --build -d
   ```

3. **Verify Health**:
   - Dashboard: `http://localhost:3000`
   - API Docs: `http://localhost:8000/docs`
   - MLflow: `http://localhost:5000`

## Troubleshooting

- **Browser Crashes**: Usually due to insufficient memory in the container. Check the calculated limits in `docker-compose.yml`.
- **Port Conflicts**: Ensure ports 3000, 5000, and 8000 are not occupied by local processes.
