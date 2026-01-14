## Setting Up Read the Docs

The ivory project documentation is hosted at https://ivory.readthedocs.io/

### For Maintainers

If you need to configure Read the Docs:

1. Log in to https://readthedocs.org/ with your GitHub account
2. Import the `meerklass/ivory` repository if not already connected
3. The `.readthedocs.yaml` configuration file controls the build settings

### Taking Over Existing Documentation

If https://ivory.readthedocs.io/ exists but is not connected to the current repository:

**Option 1: Contact Read the Docs Support**
- Email support@readthedocs.org with:
  - Project name: ivory
  - Repository: https://github.com/meerklass/ivory
  - Proof of ownership (maintainer status on the GitHub repo)
  - Request to transfer ownership or re-import

**Option 2: Use a Different Subdomain**
- Import as `meerklass-ivory` or `ivory-workflow`
- Update links in README.rst to point to new URL

**Option 3: Coordinate with Original Owner**
- Find the original owner through Read the Docs project page
- Request transfer or addition as maintainer
- Update repository connection

### Automated Documentation Building

Documentation is automatically built on:
- Every push to `main` branch (via Read the Docs webhook)
- Every pull request (via GitHub Actions)

The GitHub Actions workflow (`.github/workflows/tests.yml`) includes a `docs` job that:
- Builds documentation with Sphinx
- Uploads HTML artifacts for PR previews
- Validates that documentation builds successfully

### Local Documentation Building

To build documentation locally:

```bash
cd docs
pip install -r requirements.txt
make html
```

View the built documentation at `docs/_build/html/index.html`
