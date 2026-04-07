# Yfinance Backend Documentation

## Overview

This Django backend provides a complete infrastructure for fetching, caching, and serving stock data from yfinance. The system includes:

- **Models** for storing stock information and historical price data
- **Service layer** for yfinance operations with intelligent caching
- **API endpoints** for data retrieval and synchronization
- **Admin interface** for managing stocks
- **Management commands** for batch operations

## Architecture

### Models

#### Stock
Stores basic stock information:
- `symbol` (PK): Unique stock symbol (e.g., 'ABEV3.SA')
- `name`: Company name
- `currency`: Currency code (default: BRL)
- `market`: Market information
- `created_at`, `updated_at`: Timestamps

#### StockPrice
Stores historical price data:
- `stock` (FK): Reference to Stock
- `date`: Trading date (indexed)
- `open`, `high`, `low`, `close`: OHLC prices
- `volume`: Trading volume
- `adj_close`: Adjusted closing price
- Unique constraint on (stock, date) for data integrity

#### StockDataSync
Tracks synchronization status:
- `stock` (OneToOne): Reference to Stock
- `last_sync`: When data was last updated
- `next_sync`: When data should be updated next
- `sync_status`: Current status (pending/syncing/completed/failed)
- `error_message`: Error details if sync fails

### Service Layer (services.py)

**YfinanceService** provides these main methods:

1. **fetch_stock_data(symbol, days=365)**
   - Downloads data from yfinance
   - Returns pandas DataFrame

2. **sync_stock_data(symbol, days=365)**
   - Fetches from yfinance and saves to database
   - Handles transactions and error handling
   - Updates sync status
   - Returns: (success: bool, message: str, record_count: int)

3. **get_stock_prices(symbol, days=365)**
   - Retrieves cached data from database
   - Returns QuerySet of StockPrice objects

4. **get_stock_chart_data(symbol, days=365)**
   - Returns formatted data for CanvasJS chart
   - Includes candlestick points and table data
   - Perfect for frontend consumption

5. **sync_all_stocks(days=365)**
   - Syncs all configured stocks
   - Returns: Dict with results for each stock

6. **is_data_cached(symbol)**
   - Checks if data exists in database
   - Returns: bool

### API Endpoints

#### GET /api/stock-data/
Retrieves stock data for the chart

**Parameters:**
- `symbol`: Stock symbol (e.g., 'ABEV3.SA')

**Response:**
```json
{
  "symbol": "ABEV3.SA",
  "candlestick_points": [
    {
      "x": 1609459200000,
      "y": [101.95, 112.84, 89.37, 112.21]
    }
  ],
  "table_data": [
    {
      "date": "2021-01-01",
      "open": 101.95,
      "high": 112.84,
      "low": 89.37,
      "close": 112.21,
      "volume": 45500000
    }
  ],
  "record_count": 365
}
```

**Behavior:**
- Tries to get data from database first
- If not found, fetches from yfinance and caches it
- Automatic fallback to live data if not cached

#### POST /api/sync-stock/
Manually trigger data synchronization

**Request:**
```json
{
  "symbol": "ABEV3.SA"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully synced 252 records for ABEV3.SA",
  "record_count": 252,
  "symbol": "ABEV3.SA"
}
```

**Special:**
- Use `"symbol": "all"` to sync all configured stocks

#### GET /api/stocks/
List all available stocks with sync status

**Response:**
```json
{
  "stocks": [
    {
      "symbol": "ABEV3.SA",
      "name": "Ambev",
      "currency": "BRL",
      "price_count": 252,
      "sync_info": {
        "status": "completed",
        "last_sync": "2024-01-15T10:30:00Z",
        "next_sync": "2024-01-16T10:30:00Z"
      }
    }
  ],
  "total": 10
}
```

## Management Commands

### fetch_stock_data

Fetch and cache stock data from yfinance

**Usage:**
```bash
# Fetch default stock (ABEV3.SA)
python manage.py fetch_stock_data

# Fetch specific stock
python manage.py fetch_stock_data --symbol PETR4.SA

# Fetch all configured stocks
python manage.py fetch_stock_data --all

# Fetch custom period
python manage.py fetch_stock_data --symbol VALE3.SA --days 500
```

**Options:**
- `--symbol`: Specific stock symbol
- `--days`: Number of days of historical data (default: 365)
- `--all`: Sync all configured stocks

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Ensure requirements.txt contains:
```
Django==6.0.3
yfinance==0.2.36
pandas==2.0.3
requests==2.31.0
```

### 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Initial Data Load
```bash
# Load all stocks
python manage.py fetch_stock_data --all

# Or load one at a time
python manage.py fetch_stock_data --symbol ABEV3.SA
```

### 4. Admin Interface
Create a superuser and access Django admin:
```bash
python manage.py createsuperuser
# Visit http://localhost:8000/admin
```

In the admin interface, you can:
- View and manage stocks
- Monitor sync status
- Browse historical price data
- Search and filter stocks

## Usage Examples

### Python/Django Shell
```python
from index.services import YfinanceService

# Get formatted chart data
data = YfinanceService.get_stock_chart_data('ABEV3.SA')

# Manual sync
success, msg, count = YfinanceService.sync_stock_data('PETR4.SA')

# Check if cached
cached = YfinanceService.is_data_cached('VALE3.SA')
```

### Frontend JavaScript
```javascript
// Fetch stock data
fetch('/api/stock-data/?symbol=ABEV3.SA')
  .then(r => r.json())
  .then(data => {
    // data.candlestick_points
    // data.table_data
  });

// Trigger manual sync
fetch('/api/sync-stock/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({symbol: 'PETR4.SA'})
})
  .then(r => r.json());
```

## Configured Stocks

The backend supports these Brazilian stocks:
- ABEV3.SA (Ambev)
- PETR4.SA (Petrobras)
- VALE3.SA (Vale)
- ITUB4.SA (Itaú)
- BBDC4.SA (Bradesco)
- BBAS3.SA (Banco do Brasil)
- MGLU3.SA (Magazine Luiza)
- GGBR4.SA (Gerdau)
- WEGE3.SA (WEG)
- LREN3.SA (Lojas Renner)

## Performance Considerations

### Database Indexes
- `(stock, date)` for efficient historical queries
- `(stock, -date)` for reverse chronological access

### Caching Strategy
- Data is cached in the database after first fetch
- Subsequent requests served from cache (instant)
- Sync status tracking prevents redundant downloads

### Data Volume
- ~252 trading days per year
- Each stock stores: date, O, H, L, C, volume, adj_close
- Minimal database footprint (~2KB per record)

## Troubleshooting

### No data returned from API
1. Check if stock is synced: `/api/stocks/`
2. Manually trigger sync: `/api/sync-stock/`
3. Check sync status in Django admin

### Import errors
- Ensure all packages installed: `pip install -r requirements.txt`
- Check Python version compatibility (3.8+)

### Migration issues
```bash
python manage.py makemigrations --empty index --name fix_issue
python manage.py migrate
```

## Security Notes

- API endpoints are read-only (GET)
- Sync endpoint should be restricted in production
- No authentication enforced in current implementation (add as needed)
- yfinance API has rate limits (~2000 requests/hour)

## Future Enhancements

- [ ] Celery tasks for automatic periodic syncing
- [ ] WebSocket support for real-time updates
- [ ] Email alerts for price changes
- [ ] Advanced technical indicators
- [ ] API rate limiting and caching headers
- [ ] Authentication and user permissions
- [ ] Support for cryptocurrency and forex
