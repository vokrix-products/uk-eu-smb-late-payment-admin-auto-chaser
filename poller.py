import os, sys, time, json, uuid, logging
import requests
from pathlib import Path

# Ensure we can import processor from the backend folder
sys.path.insert(0, 'backend')
import processor  # assuming processor.py has a process() function

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

SUPABASE_URL = os.environ['SUPABASE_URL'].rstrip('/')
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_KEY']
PRODUCT_ID = os.environ['PRODUCT_ID']
ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def supabase_rest(path, method='GET', json=None, params=None):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    resp = requests.request(method, url, headers=HEADERS, json=json, params=params)
    resp.raise_for_status()
    return resp

def download_from_bucket(bucket, file_path, dest):
    url = f"{SUPABASE_URL}/storage/v1/object/authenticated/{bucket}/{file_path}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    with open(dest, 'wb') as f:
        f.write(r.content)

def upload_to_bucket(bucket, file_path, src_path):
    with open(src_path, 'rb') as f:
        files = {'file': f}
        url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}"
        # Use resumable upload for large files
        r = requests.post(url, headers={'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}, files=files)
        r.raise_for_status()
    return url

def poll():
    params = {
        'status': 'eq.pending',
        'job_type': 'eq.process_upload',
        'product_id': f'eq.{PRODUCT_ID}',
        'select': '*',
        'order': 'created_at.asc',
        'limit': '1'
    }
    jobs = supabase_rest('jobs', params=params).json()
    if not jobs:
        return
    job = jobs[0]
    job_id = job['id']
    logger.info(f'Processing job {job_id}')
    try:
        # Dowload uploaded file
        input_path = Path('/tmp') / (job_id + '_input')
        file_path_in_bucket = job.get('file_path') or job.get('input_file_path')
        if not file_path_in_bucket:
            raise Exception("No file_path in job record")
        download_from_bucket('uploads', file_path_in_bucket, input_path)
        
        # Run processor
        with open(input_path, "rb") as f:
            file_bytes = f.read()
        records = processor.process_file(file_bytes)  # adapt call to your processor signature
        # records is a list of dicts expected keys: product_id, customer_id, title, status, details, source_file_path, due_date
        
        # Insert records into 'records' table
        for rec in records:
            rec['product_id'] = PRODUCT_ID
            rec['customer_id'] = job.get('customer_id', '')
            rec.setdefault('title', '')
            details = rec.setdefault('details', {})
            rec.setdefault('source_file_path', file_path_in_bucket)
            # Extract due_date from details if not top-level
            if 'due_date' not in rec or rec['due_date'] is None:
                rec['due_date'] = details.pop('due_date', None)
            else:
                details.pop('due_date', None)
            supabase_rest('records', method='POST', json=rec)
        
        # Generate result summary
        result_summary = f"Processed {len(records)} records."
        result_file = Path('/tmp') / (job_id + '_result.csv')
        result_file.write_text('\n'.join([','.join([str(v) for v in rec.values()]) for rec in records]))
        # Upload result to results bucket
        result_path = f"{job_id}/result.csv"
        upload_to_bucket('results', result_path, result_file)
        
        # Update job to completed
        supabase_rest(f'jobs?id=eq.{job_id}', method='PATCH', json={
            'status': 'completed',
            'output_file_path': result_path,
            'result_summary': result_summary,
            'completed_at': 'now()'
        })
        logger.info(f'Job {job_id} completed successfully')
    except Exception as e:
        logger.error(f'Job {job_id} failed: {str(e)}')
        supabase_rest(f'jobs?id=eq.{job_id}', method='PATCH', json={
            'status': 'failed',
            'result_summary': str(e),
            'completed_at': 'now()'
        })

if __name__ == '__main__':
    while True:
        try:
            poll()
        except Exception as e:
            logger.error(f'Poll cycle error: {str(e)}')
        time.sleep(60)
