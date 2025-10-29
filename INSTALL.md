# Installation Guide

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install StatSQLi
pip install -e .

# 3. Start lab application
cd lab && python app.py

# 4. Run demo
python demo.py
```

## Detailed Installation

### Requirements

- **Python**: 3.8 or higher
- **pip**: Latest version
- **Operating System**: Linux, macOS, or Windows (with WSL recommended)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `requests` - HTTP library for making requests
- `numpy` - Numerical computing
- `scipy` - Statistical functions (t-tests)
- `flask` - For lab application
- `matplotlib` - For benchmark charts

### Step 2: Install StatSQLi

#### Option A: Development Installation (Recommended)

```bash
pip install -e .
```

This installs StatSQLi in "editable" mode, so code changes are immediately available.

#### Option B: Regular Installation

```bash
pip install .
```

### Step 3: Verify Installation

```bash
statsqli --help
```

You should see the StatSQLi help message.

## Lab Setup

### Option 1: Flask Application (SQLite - Easiest)

```bash
cd lab
python app.py
```

The server starts on `http://127.0.0.1:5000`

**Note**: The Flask app simulates `SLEEP()` for SQLite. For real MySQL testing, use Option 2.

### Option 2: MySQL Setup (More Realistic)

1. **Install MySQL**:
   ```bash
   # macOS
   brew install mysql
   
   # Ubuntu/Debian
   sudo apt-get install mysql-server
   ```

2. **Start MySQL**:
   ```bash
   mysql.server start  # macOS
   sudo systemctl start mysql  # Linux
   ```

3. **Create Database**:
   ```bash
   mysql -u root -p < lab/setup_mysql.sql
   ```

4. **Configure PHP Script** (if using):
   - Edit `lab/mysql_vulnerable.php`
   - Update database credentials
   - Run with PHP server: `php -S 127.0.0.1:8000 lab/mysql_vulnerable.php`

## Testing the Installation

### 1. Start Lab Application

```bash
cd lab
python app.py
# Server runs on http://127.0.0.1:5000
```

### 2. Run Demo

In another terminal:

```bash
python demo.py
```

### 3. Manual Test

```bash
statsqli "http://127.0.0.1:5000/vulnerable?id=1" \
    --payload "1 OR ({condition}) AND 1=1" \
    --table users \
    --column username \
    --where "1=1 LIMIT 0,1"
```

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`:
```bash
# Make sure you're in the project root
pwd  # Should show .../BlindSQLInjection

# Reinstall
pip install -e .
```

### Permission Errors

On Linux/macOS:
```bash
pip install --user -r requirements.txt
```

### Flask/Server Issues

If the lab app won't start:
```bash
# Check Python version
python --version  # Should be 3.8+

# Check Flask installation
pip show flask

# Try running directly
python lab/app.py
```

### Database Errors (SQLite)

If you see database errors:
```bash
# Delete old database
rm lab/vulnerable.db

# Restart lab app (it will recreate)
cd lab && python app.py
```

### Network/Connection Errors

If StatSQLi can't connect:
1. Verify lab app is running: `curl http://127.0.0.1:5000/`
2. Check firewall settings
3. Try `127.0.0.1` instead of `localhost`

## Advanced Setup

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# Install
pip install -r requirements.txt
pip install -e .
```

### Docker Setup (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["python", "lab/app.py"]
```

## Next Steps

After installation:
1. Read `README.md` for usage examples
2. Run `python demo.py` to see StatSQLi in action
3. Check `WRITEUP.md` for technical details
4. Review `benchmarks/compare_tools.py` for performance testing

## Support

If you encounter issues:
1. Check this guide
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Verify Python version (3.8+)
5. Check that lab application is running

