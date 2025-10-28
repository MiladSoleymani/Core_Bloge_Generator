# How to Check Reports in Database

Reports are automatically saved to MongoDB when generated. Here's how to check them.

## Quick Check

### 1. Show All Reports

```bash
python scripts/check_database.py
```

This shows:
- Database statistics (users, reports, KB items)
- Recent reports with details

### 2. List All Reports

```bash
python scripts/check_database.py --list-reports
```

Shows:
- Report ID
- User ID
- Patient name, age, sex
- Created date
- Generation time
- Categories

### 3. Get Specific Report

After getting a report_id from the response:

```bash
python scripts/check_database.py --report-id <report-id>
```

Shows full report details including:
- Patient information
- Assessment summary
- CVD risk summary
- Category reports

### 4. View Report in Markdown

```bash
python scripts/check_database.py --report-id <report-id> --markdown
```

Displays the full markdown-formatted report.

### 5. Export Report

```bash
python scripts/check_database.py --report-id <report-id> --export my_report.json
```

Exports complete report to JSON file.

## Using MongoDB Shell (mongosh)

### Connect to MongoDB

```bash
mongosh mongodb://localhost:27017
```

### Switch to Database

```bash
use blog_generator
```

### List Collections

```bash
show collections
```

Output:
- `users` - User records
- `medical_reports` - Generated reports
- `knowledge_base` - Health information

### View Reports

```javascript
// List all reports
db.medical_reports.find().pretty()

// Count reports
db.medical_reports.countDocuments()

// Get latest report
db.medical_reports.find().sort({created_at: -1}).limit(1).pretty()

// Find by user_id
db.medical_reports.find({user_id: "user-123"}).pretty()

// Find by report_id
db.medical_reports.findOne({report_id: "your-report-id"})

// Get only patient names
db.medical_reports.find({}, {"report_data.patient.name": 1, report_id: 1})
```

### View Users

```javascript
// List all users
db.users.find().pretty()

// Count users
db.users.countDocuments()

// Find specific user
db.users.findOne({user_id: "user-123"})
```

### View Knowledge Base

```javascript
// List categories
db.knowledge_base.distinct("category")

// Count KB items
db.knowledge_base.countDocuments()

// View one item
db.knowledge_base.findOne()
```

## Report Structure in MongoDB

### medical_reports Collection

```javascript
{
  _id: ObjectId("..."),
  report_id: "uuid",
  user_id: "user-123",
  report_data: {
    patient: {
      name: "John Doe",
      age: 45,
      sex: "male"
    },
    labs: [...],
    cvd_summary: {...},
    assessment: {...},
    plan: [...],
    red_flags: [...],
    resources_table: [...],
    category_reports: [
      {
        category: "weight_management",
        text: "...",
        sources: [...]
      }
    ],
    disclaimer: "..."
  },
  json_content: {...},
  markdown_content: "...",
  created_at: ISODate("2025-10-28T12:00:00Z"),
  generation_time_seconds: 45.2,
  tokens_used: null,
  estimated_cost: null
}
```

### users Collection

```javascript
{
  _id: ObjectId("..."),
  user_id: "user-123",
  created_at: ISODate("2025-10-28T12:00:00Z"),
  updated_at: ISODate("2025-10-28T12:30:00Z")
}
```

## Useful MongoDB Queries

### Find Reports from Last Hour

```javascript
db.medical_reports.find({
  created_at: {
    $gte: new Date(Date.now() - 3600000)
  }
})
```

### Count Reports by User

```javascript
db.medical_reports.aggregate([
  {
    $group: {
      _id: "$user_id",
      count: { $sum: 1 }
    }
  }
])
```

### Find Reports with Specific Category

```javascript
db.medical_reports.find({
  "report_data.category_reports.category": "weight_management"
})
```

### Get Report Generation Times

```javascript
db.medical_reports.find(
  {},
  {
    report_id: 1,
    generation_time_seconds: 1,
    created_at: 1
  }
).sort({created_at: -1})
```

### Delete Old Reports (Older than 30 days)

```javascript
db.medical_reports.deleteMany({
  created_at: {
    $lt: new Date(Date.now() - 30*24*60*60*1000)
  }
})
```

## Using MongoDB Compass (GUI)

1. Download MongoDB Compass: https://www.mongodb.com/products/compass
2. Connect to: `mongodb://localhost:27017`
3. Select database: `blog_generator`
4. Browse collections visually

## Backup Reports

### Export All Reports

```bash
mongoexport --db=blog_generator --collection=medical_reports --out=reports_backup.json
```

### Export Specific User's Reports

```bash
mongoexport --db=blog_generator --collection=medical_reports --query='{"user_id":"user-123"}' --out=user_reports.json
```

### Import Reports

```bash
mongoimport --db=blog_generator --collection=medical_reports --file=reports_backup.json
```

## Troubleshooting

### Cannot Connect to MongoDB

```bash
# Check if MongoDB is running
docker-compose ps mongodb

# View MongoDB logs
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb
```

### No Reports Found

1. Check worker is running: `python -m app.worker`
2. Verify request was sent: `python scripts/send_request.py`
3. Check worker logs for errors
4. Ensure knowledge base imported: `python setup_worker.py`

### Empty Category Reports

- Knowledge base not imported
- Run: `python setup_worker.py`

## Performance Tips

### Create Indexes (Already done automatically)

```javascript
// These indexes are created by the app
db.medical_reports.createIndex({report_id: 1}, {unique: true})
db.medical_reports.createIndex({user_id: 1, created_at: -1})
db.users.createIndex({user_id: 1}, {unique: true})
```

### Monitor Database Size

```javascript
db.stats()
db.medical_reports.stats()
```

### Clean Up Old Data

```javascript
// Archive reports older than 90 days
const cutoffDate = new Date(Date.now() - 90*24*60*60*1000)
db.medical_reports_archive.insertMany(
  db.medical_reports.find({created_at: {$lt: cutoffDate}}).toArray()
)
db.medical_reports.deleteMany({created_at: {$lt: cutoffDate}})
```

## Summary

**Quick commands:**
```bash
# Check all reports
python scripts/check_database.py

# Get specific report
python scripts/check_database.py --report-id <id>

# View markdown
python scripts/check_database.py --report-id <id> --markdown

# Use MongoDB shell
mongosh mongodb://localhost:27017
use blog_generator
db.medical_reports.find().pretty()
```

Reports are stored with:
- ✓ Full patient data
- ✓ AI-generated category reports
- ✓ Markdown format
- ✓ Generation metadata
- ✓ User association
