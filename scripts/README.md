# RabbitMQ Integration Scripts

Simple Python scripts for sending requests, receiving responses, and checking the database.

## Scripts

### 1. send_request.py

Send a report generation request to RabbitMQ.

**Basic Usage:**
```bash
python scripts/send_request.py
```

**With Custom User ID:**
```bash
python scripts/send_request.py --user-id user-123
```

**With Sample Data File:**
```bash
python scripts/send_request.py --sample-file data/sample_reports/Kushagra\ mandwal.json
```

**Remote RabbitMQ:**
```bash
python scripts/send_request.py --host rabbitmq.example.com
```

**Options:**
- `--host` - RabbitMQ host (default: localhost)
- `--user-id` - User identifier (default: auto-generated)
- `--sample-file` - Path to sample data JSON file

### 2. receive_response.py

Listen for and display report generation responses.

**Basic Usage:**
```bash
python scripts/receive_response.py
```

**With Timeout:**
```bash
python scripts/receive_response.py --timeout 60
```

**Remote RabbitMQ:**
```bash
python scripts/receive_response.py --host rabbitmq.example.com
```

**Options:**
- `--host` - RabbitMQ host (default: localhost)
- `--timeout` - Stop after N seconds (default: run forever)

### 3. check_database.py

Check reports and users stored in MongoDB.

**Basic Usage:**
```bash
# Show stats and recent reports
python scripts/check_database.py

# Show database statistics
python scripts/check_database.py --stats

# List all users
python scripts/check_database.py --list-users

# List all reports
python scripts/check_database.py --list-reports

# Get specific report
python scripts/check_database.py --report-id <report-id>

# Get report in markdown format
python scripts/check_database.py --report-id <report-id> --markdown

# Export report to JSON
python scripts/check_database.py --report-id <report-id> --export report.json

# Filter reports by user
python scripts/check_database.py --list-reports --user-id user-123
```

**Options:**
- `--stats` - Show database statistics
- `--list-users` - List all users
- `--list-reports` - List all reports
- `--report-id` - Get specific report by ID
- `--user-id` - Filter reports by user ID
- `--markdown` - Show report in markdown format
- `--export` - Export report to JSON file

## Quick Test

**Terminal 1 - Start Worker:**
```bash
python -m app.worker
```

**Terminal 2 - Listen for Responses:**
```bash
python scripts/receive_response.py
```

**Terminal 3 - Send Request:**
```bash
python scripts/send_request.py
```

You should see:
1. Terminal 3: Request sent confirmation
2. Terminal 1: Worker processing the request
3. Terminal 2: Response received with report ID

## Integration Example

### In Your Backend Application

**Send Request:**
```python
from scripts.send_request import send_request

# Send request and get request_id
request_id = send_request(
    host='localhost',
    user_id='user-123',
    sample_file='path/to/patient_data.json'
)

print(f"Request sent: {request_id}")
```

**Receive Responses (Background Service):**
```python
import pika
import json

def handle_response(ch, method, properties, body):
    response = json.loads(body)

    if response['status'] == 'success':
        report_id = response['report_id']
        user_id = response['user_id']

        # Store report_id in your database
        # Notify user
        # Fetch full report from MongoDB if needed
        print(f"Report ready for user {user_id}: {report_id}")
    else:
        # Handle error
        print(f"Error: {response['error_message']}")

# Set up consumer
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)
channel = connection.channel()

channel.basic_consume(
    queue='report_generation_responses',
    on_message_callback=handle_response,
    auto_ack=True
)

channel.start_consuming()
```

## Message Format

### Request Message
```json
{
  "request_id": "uuid-v4",
  "user_id": "user-123",
  "patient": {
    "name": "John Doe",
    "age": 45,
    "sex": "male"
  },
  "labs": [...],
  "cvd_summary": {...},
  "assessment": {...},
  "plan": [...],
  "red_flags": [...],
  "resources_table": [...],
  "disclaimer": "..."
}
```

### Response Message
```json
{
  "request_id": "uuid-v4",
  "user_id": "user-123",
  "report_id": "generated-uuid",
  "status": "success",
  "error_message": null,
  "timestamp": "2025-10-28T12:00:00Z"
}
```

## Error Handling

Both scripts handle common errors:

**RabbitMQ Connection Failed:**
```
✗ Error: Could not connect to RabbitMQ
Make sure RabbitMQ is running:
  docker-compose up -d rabbitmq
```

**Invalid Message Format:**
- `send_request.py`: Validates required fields
- `receive_response.py`: Handles JSON decode errors

## Dependencies

These scripts use `pika` for RabbitMQ:

```bash
pip install pika
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

## Production Considerations

For production use:
1. Add error handling and retry logic
2. Use connection pooling
3. Implement message acknowledgment
4. Add logging
5. Use environment variables for configuration
6. Consider using async consumers (aio-pika)

## Troubleshooting

**Queue Not Found:**
```bash
# Declare queues manually
python -c "
import pika
conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
ch = conn.channel()
ch.queue_declare('report_generation_requests', durable=True)
ch.queue_declare('report_generation_responses', durable=True)
conn.close()
"
```

**Connection Refused:**
- Check RabbitMQ is running: `docker-compose ps rabbitmq`
- Verify port 5672 is accessible
- Check firewall settings

**No Response Received:**
- Ensure worker is running: `python -m app.worker`
- Check worker logs for errors
- Verify knowledge base is imported: `python tests/setup_worker.py`

## Advanced Usage

### Batch Processing

Send multiple requests:
```bash
for i in {1..10}; do
    python scripts/send_request.py --user-id "user-$i"
    sleep 1
done
```

### Monitor Queue

Check queue depth:
```bash
curl -u guest:guest http://localhost:15672/api/queues/%2F/report_generation_requests
```

### Custom Configuration

Create a config file:
```python
# config.py
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'
REQUEST_QUEUE = 'report_generation_requests'
RESPONSE_QUEUE = 'report_generation_responses'
```

Then use in scripts:
```python
from config import RABBITMQ_HOST, REQUEST_QUEUE

connection = pika.BlockingConnection(
    pika.ConnectionParameters(RABBITMQ_HOST)
)
```
