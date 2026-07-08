python -m pytest
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

python -m ruff check .
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}