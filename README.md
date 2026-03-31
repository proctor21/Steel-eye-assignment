# SteelEye ESMA FIRDS Pipeline

A Python data pipeline that downloads, parses, transforms, and stores ESMA FIRDS DLTINS financial instrument data.

## Pipeline Steps

1. Download ESMA FIRDS index XML
2. Extract the second DLTINS download link
3. Download and unzip the DLTINS file
4. Parse XML into a DataFrame
5. Add `a_count` and `contains_a` derived columns
6. Save output CSV to local, S3, or Azure Blob via `fsspec`

## Setup
```bash
pip install -r requirements.txt
```

## Run
```bash
# Local output (default)
python main.py

# AWS S3
python main.py --output s3://my-bucket/output/data.csv

# Azure Blob
python main.py --output az://my-container/output/data.csv
```

## Tests
```bash
pytest tests/ -v
```

## Project Structure
```
├── src/
│   ├── downloader.py   # Downloads index XML and DLTINS ZIP
│   ├── parser.py       # Parses index XML and DLTINS XML
│   ├── transformer.py  # Adds a_count and contains_a columns
│   └── storage.py      # Cloud-agnostic CSV storage via fsspec
├── tests/              # Unit tests for all modules
├── main.py             # Pipeline entry point
└── requirements.txt
```

## Cloud Storage

| Destination | URI format | Extra deps |
|---|---|---|
| Local | `output/data.csv` | – |
| AWS S3 | `s3://bucket/path/data.csv` | `s3fs` |
| Azure Blob | `az://container/path/data.csv` | `adlfs` |
