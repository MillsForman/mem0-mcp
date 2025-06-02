# Plan: Deploying a Fork of `mem0ai/mem0-mcp` to AWS App Runner for Cursor MCP Integration

**Goal:** Fork the official `mem0ai/mem0-mcp` Python server, deploy this fork to AWS App Runner to provide a headless, cloud-based MCP SSE endpoint that Cursor can connect to.

**References:**
*   Original `mem0ai/mem0-mcp` GitHub Repository: [https://github.com/mem0ai/mem0-mcp](https://github.com/mem0ai/mem0-mcp)
*   Cursor MCP Integration Guide (for context): [https://docs.mem0.ai/integrations/mcp-server](https://docs.mem0.ai/integrations/mcp-server)

---

## Phase 1: Fork, Clone, and Prepare Your `mem0-mcp` Repository

**Task 1.1: Fork the `mem0ai/mem0-mcp` Repository on GitHub**
*   **Action:**
    1.  Navigate to [https://github.com/mem0ai/mem0-mcp](https://github.com/mem0ai/mem0-mcp).
    2.  Click the **"Fork"** button and select your GitHub account as the destination.
*   **Result:** You will have a personal copy, e.g., `https://github.com/YourGitHubUsername/mem0-mcp`.

**Task 1.2: Clone Your Forked Repository Locally**
*   **Action:**
    1.  Go to your forked repository page (e.g., `https://github.com/YourGitHubUsername/mem0-mcp`).
    2.  Click "<> Code" and copy the clone URL.
    3.  In your terminal, navigate to a suitable directory for new projects and clone:
        ```bash
        git clone https://github.com/YourGitHubUsername/mem0-mcp.git
        cd mem0-mcp
        ```

**Task 1.3: Inspect Configuration and Prepare for Local Testing**
*   **Action (within your local `mem0-mcp` fork directory):**
    *   **Inspect `main.py` and `pyproject.toml`:** Understand dependencies and how the server uses the `mem0` library. Determine if `ORG_ID` and `PROJECT_ID` are required in addition to `MEM0_API_KEY` for the `MemoryClient` initialization (they likely are).
    *   **Create `.env` file:** Copy `.env.example` to `.env` (if it exists) or create `.env` from scratch.
        ```env
        MEM0_API_KEY=your_actual_mem0_platform_api_key
        MEM0_ORG_ID=org_6c7gYKa25e2wgGq9rexDAsWFEllT5p4YB49pcGKu
        MEM0_PROJECT_ID=proj_XYo87A5MWDlOEk1Gwf1tpJuAbICDsGIpkPDB0PhP
        # HOST=0.0.0.0 # Optional: for local testing
        # PORT=8080    # Optional: for local testing
        ```
    *   **Ensure `.env` is in `.gitignore`:** Add it if not already present to prevent committing secrets.

**Task 1.4: Verify Local Execution of Your Fork (Optional but Recommended)**
*   **Action (within your local `mem0-mcp` fork directory):**
    1.  Set up the Python environment using `uv` as per the original `mem0ai/mem0-mcp` README:
        ```bash
        uv venv 
        source .venv/bin/activate
        uv pip install -e .
        ```
    2.  Run the server: `uv run main.py`.
*   **Test:** Access `http://localhost:8080/sse` (or your configured port). Confirm it's responsive and that your `.env` variables are being used correctly (e.g., by checking logs or basic functionality if possible).
*   **Purpose:** Confirm the application (your fork) works with your Mem0 Platform credentials before containerizing.

--- 

## Phase 2: Containerize Your Forked `mem0-mcp` Application

**Task 2.1: Add/Confirm `Dockerfile` in Your Fork**
*   **Action:** In the root of your forked `mem0-mcp` directory, create/ensure you have the `Dockerfile`:
*   **Content (same as previously discussed):**
    ```dockerfile
    # Use an official Python runtime as a parent image
    FROM python:3.11-slim

    # Set environment variables for Python
    ENV PYTHONDONTWRITEBYTECODE 1
    ENV PYTHONUNBUFFERED 1

    # Install uv (Python package manager used by mem0-mcp)
    RUN pip install uv

    # Set the working directory in the container
    WORKDIR /app

    # Copy the project files into the container
    COPY pyproject.toml uv.lock* ./ 
    RUN uv pip install --system -e . --no-cache-dir

    # Copy the rest of the application code
    COPY . .

    # Expose the port the app runs on (default is 8080 for mem0-mcp)
    EXPOSE 8080

    # Define the command to run the application
    CMD ["uv", "run", "main.py", "--host", "0.0.0.0", "--port", "8080"]
    ```

**Task 2.2: Build and Test the Docker Image Locally (Optional but Recommended)**
*   **Action (within your local `mem0-mcp` fork directory):**
    *   Build the image: `docker build -t mem0-mcp-server-fork .`
    *   Run the container, passing necessary environment variables:
        ```bash
        docker run -p 8080:8080 \
          -e MEM0_API_KEY="m0-QQ2AeGRgQRbsz0hbIbFzflW7A2F80cii7geFdo6B" \
          -e MEM0_ORG_ID="org_6c7gYKa25e2wgGq9rexDAsWFEllT5p4YB49pcGKu" \
          -e MEM0_PROJECT_ID="proj_tuMFnQ6FBFYPsSKKq5gLe0uNHqrRRzakDoWmGS0a" \
          mem0-mcp-server-fork
        ```
*   **Test:** Access `http://localhost:8080/sse` to verify.

**Task 2.3: Commit and Push `Dockerfile` to Your Fork**
*   **Action (within your local `mem0-mcp` fork directory):**
    ```bash
    git add Dockerfile .gitignore
    git commit -m "feat: Add Dockerfile for App Runner deployment"
    git push origin main
    ```

--- 

## Phase 3: Deploy Your Fork to AWS App Runner

**Task 3.1: Choose Deployment Source for App Runner**
*   **Decision Point:** You will deploy to App Runner from your forked GitHub repository (`YourGitHubUsername/mem0-mcp`) which now contains the `Dockerfile`.

**Task 3.2: Create and Configure AWS App Runner Service**
*   **Action:** Go to AWS Console -> AWS App Runner -> "Create service".
*   **Source and deployment:**
    *   **Source:** Choose "Source code repository".
    *   Connect to your GitHub account (if not already) and select your forked repository (e.g., `YourGitHubUsername/mem0-mcp`) and the branch (e.g., `main`).
    *   **Deployment settings:** Choose "Automatic" for CI/CD on pushes to the branch, or "Manual" for initial setup.
*   **Build settings:**
    *   Choose "Configure all settings here".
    *   **Build command:** App Runner should detect the `Dockerfile`. If manual configuration is needed, ensure it points to building the Docker image.
    *   **Start command:** App Runner should use the `CMD` from your `Dockerfile`.
*   **Service configuration (same as before, repeated for clarity):**
    *   **Service name:** e.g., `mem0-mcp-forked-service`
    *   **Virtual CPU & Memory:** Defaults (e.g., 1 vCPU, 2 GB RAM).
    *   **Port:** `8080`.
    *   **Environment variables:**
        *   `MEM0_API_KEY`: `m0-QQ2AeGRgQRbsz0hbIbFzflW7A2F80cii7geFdo6B`
        *   `MEM0_ORG_ID`: `org_6c7gYKa25e2wgGq9rexDAsWFEllT5p4YB49pcGKu`
        *   `MEM0_PROJECT_ID`: `proj_tuMFnQ6FBFYPsSKKq5gLe0uNHqrRRzakDoWmGS0a`
        *   `PYTHONUNBUFFERED`: `1`
        *   `HOST`: `0.0.0.0` (though `CMD` in Dockerfile sets this)
        *   Consider using AWS Secrets Manager integration for App Runner for `MEM0_API_KEY` for better security later.
*   **Health checks:**
    *   Configure a health check. If the `mem0ai/mem0-mcp` application has a simple HTTP GET endpoint (e.g., a root path `/` or a specific `/health`), use that. Path: `/` or `/health` (if available). Interval: e.g., 30s. Timeout: e.g., 5s.
    *   If not, you might need to add one to `main.py` in your fork for reliable health checks.
        ```python
        # In main.py of your fork, if using FastAPI:
        # from fastapi import FastAPI
        # app = FastAPI() # Assuming app is your FastAPI instance
        # @app.get("/healthz") # Using /healthz as common practice
        # async def health_check():
        #     return {"status": "ok"}
        ```
    *   Commit & push this change to your fork if you add it, before App Runner builds.
*   **Security, Networking:** Review defaults.
*   **Review and Create.**
*   **Note the Default Domain:** (e.g., `https://<some-id>.<region>.awsapprunner.com`).

--- 

## Phase 4: Configure Cursor and Test

**Task 4.1: Configure Cursor**
*   **Action:**
    1.  Open Cursor IDE.
    2.  Navigate to `Settings` > `Cursor Settings` > `Features` > `MCP Servers`.
    3.  Click on `Add new MCP server`.
    4.  **Name:** e.g., `Mem0 Cloud Fork (AppRunner)`
    5.  **Type:** `sse`
    6.  **SSE Endpoint:** `https://<your-app-runner-default-domain-for-fork>/sse`.
*   **Save and Restart Cursor.**

**Task 4.2: Test the Integration**
*   **Action:** Use Cursor with your new cloud MCP server.
*   **Monitor:** Check App Runner logs and Cursor for behavior.

--- 

## Phase 5: Refinements and Considerations (Ongoing)

**(This phase remains the same as the original plan.)**

*   Authentication for App Runner Endpoint.
*   Cost Management.
*   Logging and Monitoring.
*   Custom Domain.
*   CI/CD for your forked `mem0-mcp` (e.g., a GitHub Action in your forked repo to deploy to App Runner on pushes to main, if not using App Runner's direct GitHub integration for CI/CD).

---

This plan provides a comprehensive roadmap. Each task may have sub-details discoverable during implementation (e.g., specific library versions, exact FastAPI routing in `mem0ai/mem0-mcp`).
