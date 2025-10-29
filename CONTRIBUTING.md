# Contributing to StatSQLi

Thank you for your interest in contributing to StatSQLi!

## Development Setup

1. Clone the repository
2. Install dependencies in development mode:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Testing

Run the vulnerable lab application:
```bash
cd lab
python app.py
```

Then test extraction:
```bash
statsqli "http://127.0.0.1:5000/vulnerable?id=1" --payload "' OR ({condition}) AND SLEEP(2) -- -"
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to public functions
- Keep functions focused and testable

## Areas for Contribution

1. **Database Support**: Add PostgreSQL (`pg_sleep`), SQL Server (`WAITFOR DELAY`) support
2. **Statistics**: Implement additional statistical tests (Mann-Whitney U, etc.)
3. **Optimization**: Improve parallel extraction efficiency
4. **Documentation**: Expand examples and use cases

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request with a clear description

