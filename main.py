
from pydantic import BaseModel,EmailStr
from typing import Optional,List
import os,requests,re,json
from ibm_cloud_sdk_core import IAMTokenManager
from dotenv import load_dotenv
from services.sql_rest_executor import execute_sql_rest, init_mysql_connection,extract_top_rows_html,send_email,no_send_email
from examples.few_shot_examples import example_pairs
from prompts.system_prompt_template import MYSQL_SYSTEM_PROMPT_TEMPLATE,POSTGRES_SYSTEM_PROMPT_TEMPLATE,SQL_SYSTEM_PROMPT_TEMPLATE,SCHEMA_LLM_SUMMARY_PROMPT,SQL_EXECUTION_FEEDBACK_TEMPLATE

from fastapi import UploadFile, File, HTTPException,APIRouter,FastAPI, Request
from fastapi.responses import JSONResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

SCHEMA_TARGET_PATH = "db/db_schema.txt"
# Load environment variables
load_dotenv()

wx_api_key = os.getenv('wx_api_key')
wx_service_url = os.getenv('wx_service_url')
wx_project_id = os.getenv('wx_project_id')

wx_model_id=os.getenv('wx_model_id')
wx_model_param_max_tokens=os.getenv('wx_model_param_max_tokens')

# Prepare few-shot examples
schema_file_path = "db/db_schema.txt"
schema_summary_file="db/db_schema_llm_summary.txt"

db_engine = os.getenv('DB_ENGINE', '').lower()
if db_engine == 'mysql':
    SYSTEM_PROMPT_TEMPLATE = MYSQL_SYSTEM_PROMPT_TEMPLATE
elif db_engine == 'postgres':
    SYSTEM_PROMPT_TEMPLATE = POSTGRES_SYSTEM_PROMPT_TEMPLATE
elif db_engine == 'mssql':
    SYSTEM_PROMPT_TEMPLATE = SQL_SYSTEM_PROMPT_TEMPLATE
else:
    raise ValueError("Invalid or missing DB_ENGINE. Must be 'mysql' or 'postgres'.")

app = FastAPI()

# Mount static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class QueryRequest(BaseModel):
    user_query: str


class SQLExecutionResult(BaseModel):
    message: str
    status: str
    xls_file: str
    top_rows_raw_format: Optional[str] = None
    top_rows_html_format: Optional[str] = None
                
class QuerySQLExecutionResponse(BaseModel):
    user_query: str
    sql: str
    result: SQLExecutionResult

class QuerySQLResponse(BaseModel):
    sql: str

class EmailRequest(BaseModel):
    email: EmailStr

class SchemaSummaryResponse(BaseModel):
    summary: str


class Prompt:
    def __init__(self, api_key, project_id, service_url):
        self.api_key = api_key
        self.project_id = project_id
        self.service_url = service_url

    def _get_access_token(self):
        return IAMTokenManager(
            apikey=self.api_key,
            url="https://iam.cloud.ibm.com/identity/token"
        ).get_token()

    def generate(self, input_text, model_id, parameters):
        access_token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            "model_id": model_id,
            "input": input_text,
            "parameters": parameters,
            "project_id": self.project_id
        }

        response = requests.post(self.service_url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()["results"][0]["generated_text"]
        else:
            return response.text


def extract_sql_code(output_text):
    output_text = output_text.replace('\\n', '\n').strip()

    # Extract SQL from fenced block
    match = re.search(r"```(?:sql)?\s*(.*?)\s*```", output_text, re.DOTALL)
    sql_code = match.group(1).strip() if match else output_text.strip()

    # Take only first query before next semicolon + possible SELECT keyword
    split_match = re.split(r';\s*(?=SELECT)', sql_code, flags=re.IGNORECASE)
    first_query = split_match[0].strip()

    if not first_query.endswith(';'):
        first_query += ';'

    if not re.search(r'\b(SELECT|INSERT|UPDATE|DELETE)\b', first_query, re.IGNORECASE):
        raise ValueError("No valid SQL detected.")
    
    first_query = first_query.replace('\n', ' ')
    
    return first_query



examples_str = "\n\n".join(
    f"###\nQuestion:\n{ex['question']}\nSQL:\n```sql\n{ex['sql']}\n```"
    for ex in example_pairs )


@app.post("/upload-schema")
async def upload_schema_file(schema_file: UploadFile = File(...)):
    try:
        # Ensure it's a text file
        if not schema_file.filename.endswith(".txt"):
            raise HTTPException(status_code=400, detail="Only .txt files are accepted.")

        contents = await schema_file.read()
        decoded_content = contents.decode("utf-8")

        # Write to target file
        with open(schema_file_path, "w", encoding="utf-8") as f:
            f.write(decoded_content)

        return {"message": f"Schema file '{schema_file.filename}' uploaded successfully and saved to '{SCHEMA_TARGET_PATH}'."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    

def build_retry_prompt(original_prompt: str, error_messages: List[str]) -> str:

    feedback_blocks = ""
    for i, err in enumerate(error_messages, start=1):
        feedback_blocks += SQL_EXECUTION_FEEDBACK_TEMPLATE.format(
            attempt=i,
            error_message=err.strip()
        )
    return original_prompt.strip() + "\n" + feedback_blocks


@app.post("/generate-sql-execute-result", response_model=QuerySQLExecutionResponse)
async def generate_sql_execute(query_request: QueryRequest):
    with open(schema_file_path, "r") as file:
        schema = file.read()

    include_schema_summary = os.getenv("INCLUDE_SCHEMA_SUMMARY", "false").lower() == "true"

    if include_schema_summary:
        with open(schema_summary_file, "r") as file:
            schema_summary = file.read()
    else:
        schema_summary = "NA"
        
    # with open(schema_summary_file, "r") as file:
    #     schema_summary = file.read()


    user_query = query_request.user_query

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
    schema=schema,
    schema_summary=schema_summary,
    examples_str=examples_str,
    user_query=user_query
    )
    print("Wx prompt")
    prompt = Prompt(api_key=wx_api_key, project_id=wx_project_id, service_url=wx_service_url)
    model_id = wx_model_id
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": int(wx_model_param_max_tokens),
        "stop_sequences": ["end_of_sql","\nend_of_sql"]
        # "stop_sequences": ["```", "\n##", "\nQuestion:", "\nAnswer:"]
    }
    error_feedbacks = []
    sql_query = ""
    llm_response = ""
    max_attempts = 3

    # response = prompt.generate(system_prompt, model_id, parameters)

    for attempt in range(1, max_attempts + 1):
        print("attempt:",attempt)
        try:
            current_prompt = build_retry_prompt(system_prompt, error_feedbacks) if attempt > 1 else system_prompt
            try:
                llm_response = prompt.generate(current_prompt, model_id, parameters)
                print("llm_response:",llm_response)
                # Parse string/dict if needed
                if isinstance(llm_response, str):
                    try:
                        llm_response = json.loads(llm_response)
                    except json.JSONDecodeError:
                        raise HTTPException(status_code=400, detail="Invalid response format from LLM.")

                # Check for error in the response (common key 'errors')
                if "errors" in llm_response:
                    error_messages = "; ".join(err.get("message", "") for err in llm_response["errors"])
                    raise HTTPException(status_code=400, detail=f"LLM Error: {error_messages}")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"watsonx error: {str(e)}")
            
            sql_query = extract_sql_code(llm_response)
            print(sql_query)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"SQL Generation Error (attempt {attempt}): {str(e)}")

        # Ensure DB connection
        init_status = init_mysql_connection()
        if "200" not in init_status:
            raise HTTPException(status_code=500, detail=f"DB Init Failed: {init_status}")

        execution_response_raw = execute_sql_rest(sql_query)
        try:
            inner_result = json.loads(execution_response_raw)
            status = inner_result.get("status", "")
            if status == "OK":
                message = inner_result.get("message", "")
                xls_file = inner_result.get("xls_file", "")
                top_rows, top_rows_html = extract_top_rows_html(message)

                result = SQLExecutionResult(
                    message=message,
                    status=status,
                    xls_file=xls_file,
                    top_rows_raw_format=top_rows,
                    top_rows_html_format=top_rows_html
                )
                return QuerySQLExecutionResponse(
                    user_query=user_query,
                    sql=sql_query,
                    result=result
                )
            else:
                error_feedbacks.append(inner_result.get("message", "Unknown SQL execution error."))
        except Exception as e:
            error_feedbacks.append(f"Execution parse error: {str(e)}")
    print(error_feedbacks)
    raise HTTPException(status_code=500, detail=f"All attempts failed. Final error: {error_feedbacks[-1]}")


@app.post("/send-email")
async def send_email_handler(payload: EmailRequest):
    response_json = send_email(payload.email)
    try:
        result = json.loads(response_json)
        if result["status"] != "OK":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@app.post("/no-send-email")
async def no_send_email_handler():
    response_json = no_send_email()
    try:
        result = json.loads(response_json)
        if result["status"] != "OK":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete XLS file: {str(e)}")


@app.post("/generate-sql", response_model=QuerySQLResponse)
async def generate_sql(query_request: QueryRequest):
    with open(schema_file_path, "r") as file:
        schema = file.read()

    include_schema_summary = os.getenv("INCLUDE_SCHEMA_SUMMARY", "false").lower() == "true"

    if include_schema_summary:
        with open(schema_summary_file, "r") as file:
            schema_summary = file.read()
    else:
        schema_summary = "NA"

    # print(schema_summary)

    user_query = query_request.user_query
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
    schema=schema,
    schema_summary=schema_summary,
    examples_str=examples_str,
    user_query=user_query
    )

    prompt = Prompt(api_key=wx_api_key, project_id=wx_project_id, service_url=wx_service_url)
    model_id = wx_model_id
    print(wx_model_param_max_tokens)
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": int(wx_model_param_max_tokens),
        "stop_sequences": ["end_of_sql","\nend_of_sql"]
        # "stop_sequences": ["```", "\n##", "\nQuestion:", "\nAnswer:"]
    }
    response = prompt.generate(system_prompt, model_id, parameters)
    try:
        sql_query = extract_sql_code(response)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"SQL Generation Error: {str(e)}")
    return QuerySQLResponse(sql=sql_query)

@app.post("/execute-sql", response_model=SQLExecutionResult)
async def execute_sql_only(sql_payload: QuerySQLResponse):
    init_status = init_mysql_connection()
    if "200" not in init_status:
        raise HTTPException(status_code=500, detail=f"DB Init Failed: {init_status}")
    
    # escaped_sql_query = sql_payload.sql.replace('"', '\\"')
    escaped_sql_query = sql_payload.sql.replace('"', '\\"').replace('\n', ' ')
    # print(escaped_sql_query)
    # print(sql_payload)
    execution_response_raw = execute_sql_rest(escaped_sql_query)

    try:
        inner_result = json.loads(execution_response_raw)
        message = inner_result.get("message", "")
        status = inner_result.get("status", "")
        xls_file = inner_result.get("xls_file", "")

        # Add top rows & HTML table
        top_rows, top_rows_html = extract_top_rows_html(message)

        return SQLExecutionResult(
            message=message,
            status=status,
            xls_file=xls_file,
            top_rows_raw_format=top_rows,
            top_rows_html_format=top_rows_html
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid response format: {str(e)}")
    
@app.post("/generate-schema-summary", response_model=SchemaSummaryResponse)
async def generate_schema_summary():
    with open(schema_file_path, "r") as file:
        schema_ddl = file.read()

    system_prompt = SCHEMA_LLM_SUMMARY_PROMPT.format(schema_ddl=schema_ddl)

    prompt = Prompt(api_key=wx_api_key, project_id=wx_project_id, service_url=wx_service_url)
    model_id = wx_model_id
    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 5000
    }

    response = prompt.generate(system_prompt, model_id, parameters)
    summary_text = response.strip()

    # Write the summary back to file
    with open(schema_summary_file, "w") as summary_file:
        summary_file.write(summary_text)
    return SchemaSummaryResponse(summary=summary_text)



# Render index.html at "/"
@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route for v2 with float layout
@app.get("/v2", response_class=HTMLResponse)
async def serve_index_v2(request: Request):
    return templates.TemplateResponse("indexv2.html", {"request": request})