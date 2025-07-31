import time
import requests
from requests.exceptions import RequestException, ConnectionError
import os,json
from dotenv import load_dotenv
import re
from html import escape
from typing import Tuple
# Load .env variables only once
load_dotenv()

API_KEY = os.getenv("REST_API_KEY")
API_HOST = os.getenv("REST_API_HOST")
HEADERS = {"x-api-key": API_KEY}
DB_PARAMS = {
    "db_type": os.getenv("DB_TYPE"),
    "db_name": os.getenv("DB_NAME"),
    "db_instance": os.getenv("DB_INSTANCE"),
    "db_user": os.getenv("DB_USER"),
    "db_password": os.getenv("DB_PASSWORD"),
    "db_host": os.getenv("DB_HOST"),
    "db_port": os.getenv("DB_PORT")
}

def init_mysql_connection(retries: int = 3, backoff: float = 2.0) -> str:
    """Initialize the MySQL DB connection via REST API with retries."""
    init_url = f"{API_HOST}/init"
    
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(init_url, params=DB_PARAMS, headers=HEADERS)
            return f"Init status: {response.status_code} - {response.text}"
        except (ConnectionError, RequestException) as e:
            if attempt == retries:
                return f"Init failed after {retries} attempts: {str(e)}"
            wait_time = backoff * attempt
            print(f"[Retry {attempt}] Connection error: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)

def execute_sql_rest(sql_query: str) -> str:
    """Execute SQL query via REST API and return standardized JSON result."""

    exec_url = f"{API_HOST}/ExecuteSQL"
    try:
        response = requests.post(exec_url, params={"sql_query": sql_query}, headers=HEADERS)

        if response.status_code == 200:
            # Try to decode JSON
            try:
                data = response.json()
                return json.dumps({
                    "message": data.get("message", ""),
                    "status": data.get("status", "OK"),
                    "xls_file": data.get("xls_file", "")
                })
            except Exception:
                # If not JSON, assume raw HTML string
                return json.dumps({
                    "message": response.text,
                    "status": "OK",
                    "xls_file": ""
                })

        else:
            # Try to get meaningful message from error body
            try:
                error_data = response.json()
                error_msg = error_data.get("message", response.text)
            except Exception:
                error_msg = response.text

            return json.dumps({
                "message": error_msg,
                "status": "ERROR",
                "xls_file": ""
            })

    except Exception as e:
        return json.dumps({
            "message": f"Exception during SQL execution: {str(e)}",
            "status": "ERROR",
            "xls_file": ""
        })

import re
from html import escape

def extract_top_rows_html(message: str, max_rows: int = 15) -> tuple[str, str]:
    # Step 1: Split blocks using the box-drawing characters
    blocks = re.findall(r'╭.*?╰', message, flags=re.DOTALL)
    top_blocks = blocks[:max_rows]

    parsed_rows = []

    for block in top_blocks:
        row = {}
        # Step 2: Extract key-value pairs from <strong>Field:</strong> Value
        lines = block.splitlines()
        for line in lines:
            match = re.match(r'\s*<strong>([^<:]+):</strong>\s*(.*)', line.strip())
            if match:
                key = match.group(1).strip()
                val = match.group(2).strip()
                row[key] = val
        parsed_rows.append(row)

    # Step 3: Get all unique headers
    headers = sorted({key for row in parsed_rows for key in row.keys()})

    # Step 4: Build HTML table
    html = "<table border='1' style='border-collapse: collapse;'><thead><tr>"
    for header in headers:
        html += f"<th>{escape(header)}</th>"
    html += "</tr></thead><tbody>"

    for row in parsed_rows:
        html += "<tr>"
        for header in headers:
            html += f"<td>{escape(row.get(header, ''))}</td>"
        html += "</tr>"
    html += "</tbody></table>"

    # Join original top blocks as plain text
    top_text = "\n".join(top_blocks)

    return top_text, html

def send_email(email: str) -> str:
    """Send the generated XLS file via email."""
    send_url = f"{API_HOST}/send_email"
    try:
        response = requests.post(send_url, params={"email": email}, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            return json.dumps({
                "message": data.get("message", "Email sent successfully"),
                "status": data.get("status", "OK")
            })
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get("message", response.text)
            except Exception:
                error_msg = response.text

            return json.dumps({
                "message": error_msg,
                "status": "ERROR"
            })

    except Exception as e:
        return json.dumps({
            "message": f"Exception during email sending: {str(e)}",
            "status": "ERROR"
        })

def no_send_email() -> str:
    """Delete the generated XLS file without sending an email."""
    delete_url = f"{API_HOST}/no_send_email"
    try:
        response = requests.post(delete_url, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            return json.dumps({
                "message": data.get("message", "File deleted successfully"),
                "status": data.get("status", "OK")
            })
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get("message", response.text)
            except Exception:
                error_msg = response.text

            return json.dumps({
                "message": error_msg,
                "status": "ERROR"
            })

    except Exception as e:
        return json.dumps({
            "message": f"Exception during file deletion: {str(e)}",
            "status": "ERROR"
        })
