
# CSV to MongoDB JSON Converter 

A simple and efficient tool to convert CSV files into MongoDB-compatible JSON format. This utility parses CSV data and outputs clean JSON documents that can be directly imported into MongoDB.

---

This guide explains how to `use and customize` the CSV to MongoDB JSON Converter  script. It covers:

1. Setting input/output file paths.
2. Reading CSV fields.
3. Creating MongoDB JSON objects.
4. Writing output to JSON.



## 1. Set File Paths

`At the bottom` of the script, before running the main function, set your CSV and JSON paths:

```python
# CSV input files
INPUT_CSV = "input.csv"          # Main CSV file
PARENT_CATEGORIES_CSV = "parent.csv"  # Parent categories CSV
CHILD_CATEGORIES_CSV = "child.csv"    # Child categories CSV

# JSON output file
OUTPUT_JSON = "output.json"           # Resulting MongoDB JSON
````

* Replace these strings with the actual file locations on your system.
* The script will read these files and save the output JSON accordingly.

---

## 2. Reading CSV Fields

Inside the `convert_csv_to_mongodb` function, each row of the CSV is read:

```python
with open(input_csv, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Extract CSV fields into variables
        title = row.get('Title', '').strip()
        content = row.get('Content', '').strip()
        date = row.get('Date', '').strip()
        image_url = row.get('Image URL', '').strip()
        image_title = row.get('Image Title', '').strip()
        categories = row.get('Categories', '').strip()
        status = row.get('Status', 'published').strip()
```

### How to Customize:

* Replace the strings inside `row.get('COLUMN_NAME')` with your CSV headers.
* Add new variables for additional columns if needed.
* Remove variables you don’t want to use.

Example:

```python
post_title = row.get('Post Title', '').strip()
body_text = row.get('Body', '').strip()
image_link = row.get('Image Link', '').strip()
publish_date = row.get('Publish Date', '').strip()
```

---

## 3. Creating MongoDB JSON Objects

After reading CSV values, the script creates a MongoDB object for each row:

```python
mongo_obj = {
    "coverImage": {
        "id": "",
        "url": converted_image_url,
        "imgCaption": image_title
    },
    "title": title,
    "description": content,
    "metaKeyword": "",
    "slug": slugify(title),
    "parentCategoryId": {"$oid": parent_id},
    "childCategoryId": {"$oid": child_id} if child_id else None,
    "authorID": {"$oid": AUTHOR_ID},
    "publicationDate": publication_date,
    "status": status.lower() if status else "published",
    "views": 0
}
```

### How to Customize:

* **Rename JSON keys** to match your MongoDB collection schema.
* **Use your extracted CSV variables** to fill the values.
* **Remove unnecessary fields** or add new ones.
* Nested objects, arrays, or optional fields can be added as needed.

Example:

```python
mongo_obj = {
    "title": post_title,
    "content": body_text,
    "image": {
        "url": image_link,
        "caption": image_title
    },
    "publishedAt": publish_date,
    "authorId": {"$oid": AUTHOR_ID},
    "status": status.lower() if status else "published"
}
```

---

## 4. Writing Output JSON

At the end of the script, all MongoDB objects are saved into a JSON file:

```python
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(mongodb_objects, f, ensure_ascii=False, indent=2)
```

* `OUTPUT_JSON` determines the saved file path.
* `indent=2` makes the JSON human-readable; remove it for compact JSON.

---

## 5. Running the Script

Run the script from the command line:

```bash
python index.py
```

* The script reads the CSV files you specified.
* Converts each row into a MongoDB JSON object.
* Saves all objects to the output JSON file.

---



