# GitHub Action Setup Guide

## Docker Build and Push Workflow

This document describes how to set up and use the GitHub Action for building and pushing Docker images.

## Prerequisites

### 1. Docker Hub Account
You need a Docker Hub account to push images.
- Sign up at: https://hub.docker.com

### 2. GitHub Repository Secrets

Add the following secrets to your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

**DOCKER_USERNAME**
- Your Docker Hub username
- Example: `jorgen-simonsson`

**DOCKER_PASSWORD**
- Your Docker Hub password or access token (recommended)
- For access token:
  - Go to Docker Hub → Account Settings → Security
  - Click "New Access Token"
  - Give it a description (e.g., "GitHub Actions")
  - Copy the token and paste as the secret value

## Usage

### Running the Workflow Manually

1. **Update the version** (on your local machine):
   ```bash
   echo "1.1" > version.txt
   git add version.txt
   git commit -m "Bump version to 1.1"
   git push
   ```

2. **Trigger the workflow**:
   - Go to your GitHub repository
   - Click on **Actions** tab
   - Select **Build and Push Docker Image** workflow
   - Click **Run workflow** button
   - Choose branch (usually `main`)
   - Check/uncheck "Push to Docker registry" option
   - Click **Run workflow**

### What the Workflow Does

1. **Reads version** from `version.txt` file
2. **Builds Docker image** for multiple platforms:
   - `linux/amd64` (Intel/AMD x86_64)
   - `linux/arm64` (Raspberry Pi, ARM64)
3. **Tags the image**:
   - `{username}/sotehus-power:latest`
   - `{username}/sotehus-power:{version}` (e.g., `1.0`)
4. **Adds metadata labels**:
   - Version number
   - Image title and description
5. **Pushes to Docker Hub** (if enabled)

### Using the Published Image

Once pushed, you can use the image:

```bash
# Pull specific version
docker pull jorgen-simonsson/sotehus-power:1.0

# Pull latest
docker pull jorgen-simonsson/sotehus-power:latest

# Run the image
docker run -d \
  --name sotehus-power \
  --network sotehus \
  -p 8080:8080 \
  --env-file .env \
  jorgen-simonsson/sotehus-power:latest
```

### Updating docker-compose.yml to use published image

Replace the `build` section with `image`:

```yaml
services:
  sotehus-power:
    image: jorgen-simonsson/sotehus-power:latest  # Or specific version
    container_name: sotehus-power
    ports:
      - "8080:8080"
    # ... rest of config
```

## Version Management

### Semantic Versioning

Follow semantic versioning for releases:
- **MAJOR.MINOR.PATCH** (e.g., 1.0.0)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Update Checklist

When releasing a new version:

1. ✅ Update `version.txt`
2. ✅ Update README.md Version History section
3. ✅ Commit and push changes
4. ✅ Run GitHub Action to build and push
5. ✅ Create a Git tag (optional):
   ```bash
   git tag v1.0
   git push origin v1.0
   ```

## Troubleshooting

### Workflow Fails: "Permission denied"
- Check that DOCKER_USERNAME and DOCKER_PASSWORD secrets are set correctly
- Verify Docker Hub credentials are valid

### Workflow Fails: "version.txt not found"
- Ensure version.txt exists in repository root
- Commit and push the file

### Image not appearing on Docker Hub
- Make sure "Push to Docker registry" option was checked when running workflow
- Verify you have push permissions to the Docker Hub repository
- Check that the repository name matches your Docker Hub username

### Multi-platform build takes too long
- This is normal for multi-platform builds
- Typically takes 5-10 minutes
- Uses GitHub cache to speed up subsequent builds

## Viewing Build Results

After the workflow completes:
1. Go to Docker Hub
2. Navigate to your repository
3. Check the **Tags** tab for new tags
4. Click on a tag to see metadata labels

## Security Best Practices

1. **Use Access Tokens** instead of passwords for DOCKER_PASSWORD
2. **Rotate tokens** regularly
3. **Use read-only tokens** where possible
4. **Never commit** secrets to the repository
5. **Review** workflow runs for any exposed credentials
