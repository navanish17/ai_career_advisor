import os
import sys
import asyncio
import asyncpg
import psycopg2
from urllib.parse import urlparse

# Get DATABASE_URL
database_url = os.getenv("DATABASE_URL")

print("-" * 50)
print("🔍 DATABASE DIAGNOSTIC TOOL")
print("-" * 50)

if not database_url:
    print("❌ ERROR: DATABASE_URL environment variable is NOT set!")
    sys.exit(1)

# Mask password for logging
parsed = urlparse(database_url)
safe_url = f"{parsed.scheme}://{parsed.username}:****@{parsed.hostname}:{parsed.port}{parsed.path}"
print(f"📡 Testing connection to: {safe_url}")
print(f"   Host: {parsed.hostname}")
print(f"   User: {parsed.username}")
print(f"   Database: {parsed.path[1:]}")

# Test 1: Synchronous Connection (psycopg2)
print("\n[1/2] Testing Sync Connection (psycopg2)...")
try:
    conn = psycopg2.connect(database_url)
    conn.close()
    print("✅ SUCCESS: Psycopg2 connected successfully!")
except Exception as e:
    print(f"❌ FAILED: Psycopg2 could not connect.")
    print(f"   Error: {e}")

# Test 2: Asynchronous Connection (asyncpg)
print("\n[2/2] Testing Async Connection (asyncpg)...")
async def test_async_conn():
    try:
        # Convert sqlalchemy format (postgresql+asyncpg://) to asyncpg format (postgresql://)
        async_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(async_url)
        await conn.close()
        print("✅ SUCCESS: Asyncpg connected successfully!")
    except Exception as e:
        print(f"❌ FAILED: Asyncpg could not connect.")
        print(f"   Error: {e}")

asyncio.run(test_async_conn())

print("-" * 50)
print("🏁 DIAGNOSTIC COMPLETE")
print("-" * 50)
