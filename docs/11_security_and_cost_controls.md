# 11 – Security, Privacy and Cost Controls

## 1. Data handling

- Use synthetic data only.
- Do not add real patient data, protected health information, or confidential employer data.
- Treat names, addresses, email-like values, and NPIs in generated data as synthetic identifiers.
- Do not publish raw generated datasets to a public GitHub repository unless they have been reviewed and intentionally approved for publication.

## 2. Secrets management

Never commit:
- AWS access keys or secret keys.
- Snowflake passwords or private keys.
- `profiles.yml` containing credentials.
- `.env` files containing secrets.
- Tokens or connection strings with embedded credentials.

Use environment variables or an appropriate local secret mechanism. Commit only sanitized configuration templates.

## 3. Git exclusions

Recommended `.gitignore` entries:

```gitignore
# Secrets and local configuration
.env
.env.*
!.env.example
profiles.yml
**/profiles.yml

# Python
__pycache__/
*.py[cod]
.venv/
venv/

# dbt generated artifacts
target/
dbt_packages/
logs/

# Local data files
*.csv
*.zip
*.parquet

# macOS
.DS_Store
__MACOSX/
```


Do not exclude a file type globally if the repository intentionally needs a small approved sample file. Prefer a dedicated data directory and explicit rules.

## 4. AWS controls

- Use least-privilege IAM permissions.
- Restrict Snowflake's S3 access to the project bucket/prefix.
- Avoid public bucket access.
- Do not store credentials in Python source code.
- Review bucket lifecycle and storage settings.

## 5. Snowflake cost controls

- Use an appropriately sized warehouse for the small synthetic workload.
- Suspend the warehouse when idle.
- Set auto-suspend and auto-resume appropriately.
- Avoid unnecessary repeated full refreshes.
- Monitor warehouse usage and trial expiration.
- Avoid leaving scheduled tasks or warehouses running unintentionally.

## 6. Trial limitations

AWS and Snowflake trial/free-tier terms, quotas, and feature availability can change. Verify current account limits before implementation. Do not assume every service or feature is included in a trial.
