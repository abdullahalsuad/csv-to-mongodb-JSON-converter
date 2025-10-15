import csv
import json
import re
from datetime import datetime
from urllib.parse import urlparse

# Configuration
AUTHOR_ID = "68e3a7095be21e85e87662e2"  
DEFAULT_PARENT_CATEGORY = "অন্যান্য"

def slugify(text):
    """Convert title to slug"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text

def extract_filename_from_url(url):
    """Extract filename from URL and convert to localhost URL"""
    if not url:
        return ""
    
    # Parse URL and get the path
    parsed = urlparse(url)
    path = parsed.path
    
    # Extract filename
    filename = path.split('/')[-1]
    
    # Return new localhost URL
    return f"http://localhost:8000/uploads/{filename}"

def load_categories(parent_csv, child_csv):
    """Load parent and child categories into dictionaries"""
    parent_categories = {}
    child_categories = {}
    
    # Load parent categories
    with open(parent_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Assuming CSV has 'name' and 'id' or '_id' columns
            name = row.get('name', '').strip()
            cat_id = row.get('id', row.get('_id', '')).strip()
            if name and cat_id:
                parent_categories[name] = cat_id
    
    # Load child categories
    with open(child_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('name', '').strip()
            cat_id = row.get('id', row.get('_id', '')).strip()
            if name and cat_id:
                child_categories[name] = cat_id
    
    return parent_categories, child_categories

def parse_categories(category_string, parent_categories, child_categories):
    """Parse category string and return parent and child IDs"""
    if not category_string:
        return parent_categories.get(DEFAULT_PARENT_CATEGORY, ""), None
    
    # Remove extra whitespace
    category_string = category_string.strip()
    
    # Handle pipe separator (Example 3)
    if '|' in category_string:
        category_string = category_string.split('|')[0].strip()
    
    # Split by '>'
    parts = [part.strip() for part in category_string.split('>')]
    
    if len(parts) == 1:
        # Single category - check in parent
        cat_name = parts[0]
        if cat_name in parent_categories:
            return parent_categories[cat_name], None
        else:
            return parent_categories.get(DEFAULT_PARENT_CATEGORY, ""), None
    
    elif len(parts) == 2:
        # Two parts (Example 1)
        first_part = parts[0]
        second_part = parts[1]
        
        first_in_parent = first_part in parent_categories
        second_in_parent = second_part in parent_categories
        
        # If both in parent and one is "অন্যান্য", skip "অন্যান্য"
        if first_in_parent and second_in_parent:
            if first_part == DEFAULT_PARENT_CATEGORY:
                return parent_categories[second_part], None
            else:
                return parent_categories[first_part], None
        
        # If only first is in parent
        elif first_in_parent:
            # Check if second is in child
            if second_part in child_categories:
                return parent_categories[first_part], child_categories[second_part]
            else:
                return parent_categories[first_part], None
        
        # If only second is in parent
        elif second_in_parent:
            return parent_categories[second_part], None
        
        # Neither found
        else:
            return parent_categories.get(DEFAULT_PARENT_CATEGORY, ""), None
    
    else:
        # More than 2 parts (Example 2)
        # Keep first as parent, second as child, ignore rest
        first_part = parts[0]
        second_part = parts[1]
        
        parent_id = parent_categories.get(first_part, parent_categories.get(DEFAULT_PARENT_CATEGORY, ""))
        child_id = child_categories.get(second_part, None)
        
        return parent_id, child_id

def convert_csv_to_mongodb(input_csv, parent_csv, child_csv, output_json):
    """Main conversion function"""
    
    # Load category mappings
    parent_categories, child_categories = load_categories(parent_csv, child_csv)
    
    # Read input CSV and convert
    mongodb_objects = []
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        
        for row in reader:
            # Extract CSV fields
            title = row.get('Title', '').strip()
            content = row.get('Content', '').strip()
            date = row.get('Date', '').strip()
            image_url = row.get('Image URL', '').strip()
            image_title = row.get('Image Title', '').strip()
            categories = row.get('Categories', '').strip()
            status = row.get('Status', 'published').strip()
            
            # Parse categories
            parent_id, child_id = parse_categories(categories, parent_categories, child_categories)
            
            # Convert image URL
            converted_image_url = extract_filename_from_url(image_url)
            
            # Parse date
            try:
                if date:
                    # Try different date formats
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
                        try:
                            dt = datetime.strptime(date, fmt)
                            publication_date = dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                            break
                        except ValueError:
                            continue
                    else:
                        publication_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
                else:
                    publication_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            except:
                publication_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
            # Create MongoDB object
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
            
            mongodb_objects.append(mongo_obj)
           
    
    # Write to JSON file
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(mongodb_objects, f, ensure_ascii=False, indent=2)
    
    print(f"Conversion complete! {len(mongodb_objects)} records converted.")
    print(f"Output saved to: {output_json}")

# Usage
if __name__ == "__main__":
    # Update these file paths
    INPUT_CSV = "file.csv"
    PARENT_CATEGORIES_CSV = "parentcategories.csv"
    CHILD_CATEGORIES_CSV = "childcategories.csv"
    OUTPUT_JSON = "mongodb_data.json"
    
    convert_csv_to_mongodb(INPUT_CSV, PARENT_CATEGORIES_CSV, CHILD_CATEGORIES_CSV, OUTPUT_JSON)
