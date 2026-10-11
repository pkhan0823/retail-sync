# RetailSync - Multi-Database Cluster Console

RetailSync is a high-performance, hybrid multi-database monitoring and operational console built with Streamlit, PostgreSQL, and MongoDB. It provides real-time schema inspection, cross-engine analytical metrics, relational join resolution, and live cluster health diagnostics across distributed database nodes.

---

## System Architecture

```text
[ Client Browser / Web UI ]
            |
            v
[ Streamlit App Server ]
    |-- URL Routing Engine (?server=srv_1 | srv_2 | srv_3)
    |-- Cached Connection Pool (@st.cache_resource)
    |
    |-- PostgreSQL Client (psycopg2)
    |   |-- orders (Transactional Ledger)
    |   |-- billing (Invoice Records)
    |   |-- inventory (Stock Quantities)
    |   `-- Cross-Table SQL Joins (Unpaid Invoices)
    |
    `-- MongoDB Client (pymongo)
        |-- products (BSON Product Catalog)
        `-- reviews (BSON Feedback Collection)
```

---

## Dashboard Sections

1. **Top Scroll Progress Bar**: Visual indicator tracking scroll position through the telemetry pipeline.
2. **Sticky Navigation HUD**: Fixed quick-navigation bar providing jump links to any section on the page.
3. **Cluster Node Selector**: Interactive cards displaying active connection states, ports, and configuration details.
4. **Live Aggregate Telemetry**: Consolidated business metrics, including total orders, inventory volume, MongoDB document counts, and gross revenue.
5. **Relational Ledger**: Side-by-side inspection of PostgreSQL orders and billing tables.
6. **Stock Allocation & SQL Joins**: Real-time inventory table and automated join query detecting all unpaid billing records.
7. **Document Streams**: BSON document preview for products and user reviews.
8. **Infrastructure Health Diagnostics**: Parallel connectivity test verifying PostgreSQL socket state and MongoDB ping status across all servers.
