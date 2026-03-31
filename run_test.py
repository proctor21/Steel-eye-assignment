from src.parser import Parser   # your parser.py
from src.transformer import Transformer   # import Transformer
import os

# Paths
xml_file = "data/DLTINS_20210119_01of02.xml"

# Parse XML
parser = Parser()
df = parser.parse_xml(xml_file)
print(f"Total rows before transform: {len(df)}")
print(df.head())

# Transform Data
transformer = Transformer()
df_transformed = transformer.add_columns(df)

print("\nAfter Transformation:")
print(df_transformed.head(10))  # show first 10 rows

print(df_transformed.shape)         # Check number of rows & columns
print(df_transformed.columns)       # Verify column names
print(df_transformed.head(10))      # Inspect first few rows
print(df_transformed.isnull().sum())  # Check for missing values