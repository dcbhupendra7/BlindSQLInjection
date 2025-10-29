# Vulnerable Web Application - Lab Setup

## What Is This?

The **Vulnerable Web Application** is a **deliberately insecure** Flask application that serves as a **testing target** for StatSQLi. It simulates a real-world web application with time-based blind SQL injection vulnerabilities.

**You don't DO anything with it — you just RUN it!**

## Purpose

This application is your **lab environment** where you can:
- Test StatSQLi safely without attacking real websites
- Learn how time-based blind SQL injection works
- Benchmark StatSQLi's performance
- Demonstrate the tool in action

## How to Use It

### Step 1: Start the Vulnerable Server

```bash
cd lab
python app.py
```

**Keep this terminal open!** The server will run continuously.

You should see:
```
[*] Database initialized
[*] Starting vulnerable server on http://127.0.0.1:5000
[!] WARNING: This is a vulnerable application for testing only!
 * Running on http://127.0.0.1:5000
```

### Step 2: Verify It's Running

Open your browser and visit: `http://127.0.0.1:5000`

You should see a page saying:
- "Vulnerable Web Application"
- "This application has intentional SQL injection vulnerabilities for testing purposes."
- Endpoint: `GET /vulnerable?id=1`

**Or test with curl:**
```bash
curl http://127.0.0.1:5000/
```

### Step 3: Use StatSQLi Against It

In a **new terminal** (keep the lab app running), run:

```bash
# Run the demo
python demo.py

# Or run StatSQLi directly
statsqli "http://127.0.0.1:5000/vulnerable?id=1" \
    --payload "1 OR ({condition}) AND SLEEP(2) -- -" \
    --table users \
    --column username
```

## What the Application Contains

### Database Structure

**Users Table:**
- `id` (1, 2, 3, 4, 5)
- `username` (admin, alice, bob, charlie, diana)
- `password` (password123, alice_secret, etc.)
- `email` (admin@example.com, etc.)

**Products Table:**
- Sample product data for additional testing

### Vulnerable Endpoint

**URL:** `http://127.0.0.1:5000/vulnerable?id=1`

**Vulnerability:** 
- The `id` parameter is directly inserted into SQL without sanitization
- You can inject SQL conditions that trigger time delays
- Perfect for testing time-based blind SQL injection

**Example Attack:**
```
http://127.0.0.1:5000/vulnerable?id=1 OR (1=1) AND SLEEP(2) --
```

This will delay for 2 seconds if the condition is true.

## How It Works (Technical Details)

1. **Receives Request**: The app gets a request like `/vulnerable?id=1`
2. **Vulnerable Query**: Builds SQL query: `SELECT * FROM users WHERE id = {user_id}`
3. **Detection**: Looks for `SLEEP()` patterns in the payload
4. **Condition Evaluation**: Evaluates SQL conditions against the database
5. **Delays**: If condition is true, applies a delay using `time.sleep()`
6. **Response**: Returns JSON (blinds the attacker - no visible data)

## Important Notes

### ⚠️ Security Warning

- **DO NOT** deploy this in production
- **DO NOT** expose it to the internet
- This is **intentionally vulnerable** for testing only
- Keep it on `127.0.0.1` (localhost only)

### What You DON'T Need to Do

- ❌ Don't modify the code (unless testing different vulnerabilities)
- ❌ Don't interact with it manually (StatSQLi does that)
- ❌ Don't try to fix the vulnerability (it's intentional!)
- ❌ Don't worry about performance (it's just for testing)

### What You DO Need to Do

- ✅ Start it and leave it running
- ✅ Let StatSQLi interact with it
- ✅ Use it for benchmarking
- ✅ Demonstrate your tool with it

## Troubleshooting

### Server Won't Start

```bash
# Check if port 5000 is in use
lsof -i :5000

# Or use a different port (edit app.py)
app.run(host='127.0.0.1', port=5001)
```

### Database Errors

```bash
# Delete and recreate database
rm lab/vulnerable.db
python app.py  # Will recreate it
```

### Can't Connect from StatSQLi

1. Make sure the server is running (check terminal)
2. Verify URL: `http://127.0.0.1:5000` (not `localhost`)
3. Check firewall isn't blocking localhost
4. Try: `curl http://127.0.0.1:5000/vulnerable?id=1`

## Quick Test

Test that everything works:

```bash
# Terminal 1: Start server
cd lab && python app.py

# Terminal 2: Test connection
curl http://127.0.0.1:5000/vulnerable?id=1

# Should return JSON like:
# {"status":"ok","count":1,"time":"0.001s"}
```

## Summary

**The Vulnerable Web Application is:**
- ✅ Your testing target
- ✅ A safe lab environment
- ✅ Just a server that runs in the background
- ✅ What StatSQLi attacks during demos

**You just need to:**
1. Start it (`python app.py`)
2. Leave it running
3. Run StatSQLi against it
4. That's it!

---

**Think of it like this:** The vulnerable app is the **target**, and StatSQLi is the **tool** that extracts data from it. You're the **researcher** demonstrating how well the tool works.

