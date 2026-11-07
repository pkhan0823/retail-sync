import pandas as pd
import psycopg2
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import streamlit as st
from datetime import datetime

# --- 1. MULTI-SERVER CONFIGURATION ---

SERVERS = {
    "srv_prod": {
        "name": "Production Server1",
        "badge": "LIVE",
        "desc": "Primary operational cluster for US orders & catalog",
        "pg": {
            "host": "localhost",
            "port": "5432",
            "database": "retailsync1",
            "user": "postgres",
            "password": "0816",
        },
        "mongo": {
            "uri": "mongodb://localhost:27017/",
            "database": "e_commerce_db",
        },
    },
    "srv_backup": {
        "name": "Backup Server2",
        "badge": "REPLICA",
        "desc": "Failover replica and read-only analytical database",
        "pg": {
            "host": "localhost",
            "port": "5432",
            "database": "retailsync2",
            "user": "postgres",
            "password": "0816",
        },
        "mongo": {
            "uri": "mongodb://localhost:27017/",
            "database": "e_commerce_db",
        },
    },
    "srv_dev": {
        "name": "Server3",
        "badge": "REPLICA",
        "desc": "Development sandbox and QA testing database",
        "pg": {
            "host": "localhost",
            "port": "5432",
            "database": "retailsync3",
            "user": "postgres",
            "password": "0816",
        },
        "mongo": {
            "uri": "mongodb://localhost:27017/",
            "database": "e_commerce_db",
        },
    },
}

# --- 2. STREAMLIT UI CONFIGURATION ---

st.set_page_config(
    page_title="Multi-Server Hybrid Retail Sync Dashboard",
    layout="wide",
)

# --- ANIMATED CSS ---

st.markdown(
    """
    <style>
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(24px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes pulseGlow {
        0% {
            box-shadow: 0 0 0 0 rgba(0,188,212,0.55);
        }
        70% {
            box-shadow: 0 0 0 14px rgba(0,188,212,0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(0,188,212,0);
        }
    }

    @keyframes dotPulse {
        0%,100% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.7);
            opacity: 0.45;
        }
    }

    @keyframes shimmer {
        0% { background-position: -600px 0; }
        100% { background-position: 600px 0; }
    }

    @keyframes titleGradient {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }

    @keyframes floatY {
        0%,100% { transform: translateY(0); }
        50% { transform: translateY(-4px); }
    }

    @keyframes borderFlow {
        0% { background-position: 0% 50%; }
        100% { background-position: 300% 50%; }
    }

    .stApp {
        background: linear-gradient(
            -45deg,
            #0b0f17,
            #101826,
            #0d1b24,
            #14111f
        );
        background-size: 400% 400%;
        animation: gradientShift 22s ease infinite;
    }

    h1 {
        background: linear-gradient(
            90deg,
            #00bcd4,
            #4caf50,
            #7c4dff,
            #00bcd4
        );
        background-size: 200% auto;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titleGradient 6s linear infinite,
                   fadeInUp 0.8s ease both;
    }

    .stMarkdown p {
        animation: fadeIn 1.1s ease both;
    }

    .server-card {
        position: relative;
        overflow: hidden;
        padding: 14px 18px;
        border-radius: 12px;
        border: 1px solid #333842;
        background-color: #1e222b;
        margin-bottom: 10px;
        transition: transform 0.25s ease,
                    border-color 0.25s ease,
                    box-shadow 0.25s ease;
        text-decoration: none !important;
        display: block;
        opacity: 0;
        animation: fadeInUp 0.7s ease forwards;
    }

    .server-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: -120%;
        width: 60%;
        height: 100%;
        background: linear-gradient(
            120deg,
            transparent,
            rgba(255,255,255,0.10),
            transparent
        );
        transition: left 0.6s ease;
    }

    .server-card:hover::before {
        left: 140%;
    }

    .server-card:hover {
        transform: translateY(-5px) scale(1.015);
        border-color: #4CAF50;
        box-shadow: 0 10px 26px rgba(76,175,80,0.22);
    }

    .server-card-active {
        border: 2px solid #00bcd4 !important;
        background-color: #162a38 !important;
        animation: fadeInUp 0.7s ease forwards,
                   pulseGlow 2.4s ease-out infinite 0.8s;
    }

    .server-title {
        font-weight: 700;
        font-size: 16px;
        color: #ffffff;
        margin-bottom: 4px;
    }

    .server-desc {
        font-size: 12px;
        color: #a0aec0;
        margin-bottom: 8px;
    }

    .server-badge {
        display: inline-block;
        font-size: 11px;
        padding: 2px 10px;
        border-radius: 4px;
        background: #2d3748;
        color: #e2e8f0;
        font-weight: 600;
        letter-spacing: 0.6px;
    }

    .server-badge::before {
        content: "";
        display: inline-block;
        width: 7px;
        height: 7px;
        margin-right: 7px;
        border-radius: 50%;
        background: #4caf50;
        animation: dotPulse 1.6s ease-in-out infinite;
    }

    .server-card-active .server-badge::before {
        background: #00bcd4;
    }

    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(
            90deg,
            transparent 0%,
            #00bcd4 50%,
            transparent 100%
        ) !important;
        background-size: 600px 100% !important;
        animation: shimmer 3.2s linear infinite;
        opacity: 0.8;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #0f1420,
            #141b2a
        );
        border-right: 1px solid #222a3a;
        animation: slideInLeft 0.7s ease both;
    }

    section[data-testid="stSidebar"] a {
        transition: transform 0.2s ease, color 0.2s ease;
    }

    section[data-testid="stSidebar"] a:hover {
        transform: translateX(6px);
        color: #00bcd4 !important;
    }

    button[data-baseweb="tab"] {
        transition: transform 0.2s ease,
                    color 0.2s ease,
                    background 0.2s ease;
        border-radius: 8px 8px 0 0;
    }

    button[data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        background: rgba(0,188,212,0.10);
    }

    div[data-baseweb="tab-highlight"] {
        background: linear-gradient(
            90deg,
            #00bcd4,
            #4caf50,
            #7c4dff,
            #00bcd4
        ) !important;
        background-size: 300% 100% !important;
        animation: borderFlow 4s linear infinite;
        height: 3px !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        border: 1px solid #262d3d;
        transition: box-shadow 0.3s ease,
                    border-color 0.3s ease;
        animation: fadeInUp 0.7s ease both;
    }

    div[data-testid="stDataFrame"]:hover {
        border-color: #00bcd4;
        box-shadow: 0 8px 24px rgba(0,188,212,0.15);
    }

    div[data-testid="stMetric"] {
        padding: 14px 16px;
        border-radius: 12px;
        background: #1a2030;
        border: 1px solid #2a3246;
        transition: transform 0.25s ease,
                    box-shadow 0.25s ease;
        animation: fadeInUp 0.7s ease both;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        border-color: #4caf50;
        box-shadow: 0 10px 22px rgba(76,175,80,0.18);
    }

    div[data-testid="stMetricValue"] {
        animation: floatY 3.5s ease-in-out infinite;
    }

    div[data-testid="stAlert"] {
        animation: slideInLeft 0.6s ease both;
    }

    div[data-testid="stExpander"] {
        border-radius: 10px;
        transition: transform 0.25s ease,
                    box-shadow 0.25s ease;
        animation: fadeInUp 0.7s ease both;
    }

    div[data-testid="stExpander"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.35);
    }

    h2, h3 {
        animation: slideInLeft 0.6s ease both;
    }

    a {
        transition: color 0.2s ease;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 3. URL QUERY PARAMETER HANDLING ---

active_server_id = st.query_params.get("server", "srv_prod")

if active_server_id not in SERVERS:
    active_server_id = "srv_prod"

active_server = SERVERS[active_server_id]

# --- 4. TOP LINK NAVIGATION BAR ---

st.title("Hybrid Multi-Server Retail Sync Dashboard")

st.markdown(
    "Click any of the server links below to inspect and fetch data "
    "from that specific server:"
)

cols = st.columns(len(SERVERS))

for col, (srv_id, srv_data) in zip(cols, SERVERS.items()):
    with col:
        is_active = srv_id == active_server_id
        card_class = (
            "server-card server-card-active"
            if is_active else "server-card"
        )

        active_marker = " (Connected)" if is_active else ""
        html_card = f"""
            <a href="?server={srv_id}" target="_self"
               class="{card_class}">
                <div class="server-title">
                    {srv_data['name']}{active_marker}
                </div>
                <div class="server-desc">
                    {srv_data['desc']}
                </div>
                <span class="server-badge">
                    {srv_data['badge']}
                </span>
            </a>
        """

        st.markdown(html_card, unsafe_allow_html=True)

st.divider()

# --- 5. SIDEBAR LINKS & SERVER INFO ---

st.sidebar.header("Quick Server Links")

for srv_id, srv_data in SERVERS.items():
    icon = ">>" if srv_id == active_server_id else "-"
    st.sidebar.markdown(
        f"{icon} [{srv_data['name']}](?server={srv_id})",
        help=f"Connect to {srv_data['name']}",
    )

st.sidebar.divider()
st.sidebar.subheader("Active Server Specs")

st.sidebar.markdown(
    f"**PostgreSQL Host:** `{active_server['pg']['host']}`"
)
st.sidebar.markdown(
    f"**PostgreSQL Port:** `{active_server['pg']['port']}`"
)
st.sidebar.markdown(
    f"**PostgreSQL DB:** `{active_server['pg']['database']}`"
)
st.sidebar.markdown(
    f"**MongoDB DB:** `{active_server['mongo']['database']}`"
)

# --- 6. CONNECTION HANDLING ---

@st.cache_resource
def get_postgres_connection(host, database, user, password, port):
    connection_url = URL.create(
        "postgresql+psycopg2",
        username=user,
        password=password,
        host=host,
        port=int(port),
        database=database,
    )

    engine = create_engine(
        connection_url,
        connect_args={
            "connect_timeout": 3,
            "application_name": "RetailSyncDashboard",
        },
        pool_pre_ping=True,
    )

    with engine.connect():
        pass

    return engine


@st.cache_resource
def get_mongo_database(uri, db_name):
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=3000
    )

    client.admin.command("ping")
    return client[db_name]


pg_conn = None
mongo_db = None

try:
    pg_conn = get_postgres_connection(
        host=active_server["pg"]["host"],
        database=active_server["pg"]["database"],
        user=active_server["pg"]["user"],
        password=active_server["pg"]["password"],
        port=active_server["pg"]["port"],
    )
except Exception as e:
    st.error(
        f"Failed to connect to PostgreSQL on "
        f"{active_server['name']}: {e}"
    )

try:
    mongo_db = get_mongo_database(
        uri=active_server["mongo"]["uri"],
        db_name=active_server["mongo"]["database"],
    )
except Exception as e:
    st.error(
        f"Failed to connect to MongoDB on "
        f"{active_server['name']}: {e}"
    )

# --- 7. DATA FETCHING FUNCTIONS ---

def fetch_postgres_data(conn):
    if conn is None:
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
        )

    try:
        df_orders = pd.read_sql(
            "SELECT * FROM orders ORDER BY order_id;",
            conn
        )

        df_inventory = pd.read_sql(
            "SELECT * FROM inventory ORDER BY product_id;",
            conn
        )

        df_billing = pd.read_sql(
            "SELECT * FROM billing ORDER BY bill_id;",
            conn
        )

        join_query = """
            SELECT
                billing.bill_id,
                billing.order_id,
                billing.bill_status,
                orders.customer_id,
                orders.total_amount,
                orders.status AS order_status
            FROM billing
            JOIN orders
                ON billing.order_id = orders.order_id
            WHERE billing.bill_status = 'unpaid';
        """

        df_unpaid = pd.read_sql(join_query, conn)

        return (
            df_orders,
            df_inventory,
            df_billing,
            df_unpaid
        )

    except Exception as e:
        st.warning(f"PostgreSQL Query Error: {e}")
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
        )


def fetch_mongo_data(db):
    if db is None:
        return pd.DataFrame(), pd.DataFrame()

    try:
        df_products = pd.DataFrame(
            list(db.products.find({}, {"_id": 0}))
        )

        df_reviews = pd.DataFrame(
            list(db.reviews.find({}, {"_id": 0}))
        )

        return df_products, df_reviews

    except Exception as e:
        st.warning(f"MongoDB Query Error: {e}")
        return pd.DataFrame(), pd.DataFrame()


# --- 8. PERFORMANCE MONITORING FUNCTIONS ---

def fetch_slow_queries(conn):
    if conn is None:
        return pd.DataFrame()

    query = """
        SELECT
            pid,
            usename,
            state,
            NOW() - query_start AS execution_time,
            ROUND(
                EXTRACT(
                    EPOCH FROM (NOW() - query_start)
                )::NUMERIC,
                2
            ) AS execution_seconds,
            LEFT(query, 1000) AS query
        FROM pg_stat_activity
        WHERE state = 'active'
          AND query_start IS NOT NULL
          AND pid <> pg_backend_pid()
          AND NOW() - query_start > INTERVAL '2 seconds'
          AND datname = current_database()
        ORDER BY execution_seconds DESC;
    """

    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        st.warning(f"Slow query error: {e}")
        return pd.DataFrame()


def fetch_historical_slow_queries(conn):
    if conn is None:
        return pd.DataFrame()

    query = """
        SELECT
            calls,
            ROUND(total_exec_time::NUMERIC, 2)
                AS total_time_ms,
            ROUND(mean_exec_time::NUMERIC, 2)
                AS avg_time_ms,
            rows,
            LEFT(query, 1000) AS query
        FROM pg_stat_statements
        ORDER BY mean_exec_time DESC
        LIMIT 20;
    """

    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        st.warning(
            "Historical query statistics unavailable. "
            "Check whether pg_stat_statements is installed and enabled. "
            f"Details: {e}"
        )
        return pd.DataFrame()


def fetch_deadlock_stats(conn):
    if conn is None:
        return pd.DataFrame()

    query = """
        SELECT
            datname,
            deadlocks,
            stats_reset
        FROM pg_stat_database
        WHERE datname = current_database();
    """

    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        st.warning(f"Deadlock monitoring error: {e}")
        return pd.DataFrame()


def fetch_connection_stats(conn):
    if conn is None:
        return pd.DataFrame()

    query = """
        SELECT
            COUNT(*) AS total_connections,
            COUNT(*) FILTER (
                WHERE state = 'active'
            ) AS active_connections,
            COUNT(*) FILTER (
                WHERE state = 'idle'
            ) AS idle_connections
        FROM pg_stat_activity
        WHERE datname = current_database();
    """

    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        st.warning(f"Connection monitoring error: {e}")
        return pd.DataFrame()


# --- FETCH CURRENT SERVER DATA ---

df_orders, df_inventory, df_billing, df_unpaid = (
    fetch_postgres_data(pg_conn)
)

df_products, df_reviews = fetch_mongo_data(mongo_db)

# --- 9. DASHBOARD TABS ---

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "PostgreSQL: Orders & Billing",
    "PostgreSQL: Inventory & Unpaid Query",
    "MongoDB: Products & Reviews",
    "Unified Summary & Metrics",
    "Multi-Server Live Status",
    "Performance Monitoring",
])

# --- TAB 1: ORDERS & BILLING ---

with tab1:
    st.subheader(
        f"PostgreSQL - Orders & Billing ({active_server['name']})"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Orders (`orders`)")
        if not df_orders.empty:
            st.dataframe(
                df_orders,
                width="stretch"
            )
        else:
            st.info("No order records found on this server.")

    with col2:
        st.markdown("### Billing (`billing`)")
        if not df_billing.empty:
            st.dataframe(
                df_billing,
                width="stretch"
            )
        else:
            st.info("No billing records found on this server.")

# --- TAB 2: INVENTORY & UNPAID QUERY ---

with tab2:
    st.subheader(
        f"PostgreSQL - Inventory & Joins ({active_server['name']})"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Inventory Stock (`inventory`)")
        if not df_inventory.empty:
            st.dataframe(
                df_inventory,
                width="stretch"
            )
        else:
            st.info("No inventory records found on this server.")

    with col2:
        st.markdown("### Unpaid Bills (SQL JOIN Query)")
        if not df_unpaid.empty:
            st.dataframe(
                df_unpaid,
                width="stretch"
            )
        else:
            st.success("No unpaid bills found on this server!")

# --- TAB 3: MONGODB ---

with tab3:
    st.subheader(
        f"MongoDB - Document Collections ({active_server['name']})"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Product Catalog (`products`)")
        if not df_products.empty:
            st.dataframe(
                df_products,
                width="stretch"
            )
        else:
            st.info("No products found in MongoDB on this server.")

    with col2:
        st.markdown("### Customer Reviews (`reviews`)")
        if not df_reviews.empty:
            st.dataframe(
                df_reviews,
                width="stretch"
            )
        else:
            st.info("No customer reviews found in MongoDB on this server.")

# --- TAB 4: UNIFIED SUMMARY ---

with tab4:
    st.subheader(
        f"Cross-Database Summary for {active_server['name']}"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Postgres Orders", len(df_orders))
    col2.metric("Postgres Inventory Items", len(df_inventory))
    col3.metric("Mongo Products", len(df_products))
    col4.metric("Mongo Reviews", len(df_reviews))

    st.markdown("---")

    if not df_orders.empty and "total_amount" in df_orders.columns:
        total_rev = df_orders["total_amount"].astype(float).sum()
        st.metric(
            "Total PostgreSQL Order Revenue",
            f"${total_rev:,.2f}"
        )

# --- TAB 5: MULTI-SERVER LIVE STATUS ---

with tab5:
    st.subheader("Live Health Check for All Configured Servers")

    st.markdown(
        "Click any server link below to navigate to it directly:"
    )

    for srv_id, srv in SERVERS.items():
        with st.expander(
            f"Server: {srv['name']} ({srv['badge']})",
            expanded=(srv_id == active_server_id),
        ):
            col_a, col_b, col_c = st.columns([2, 2, 1])

            # PostgreSQL health check
            with col_a:
                try:
                    test_p = psycopg2.connect(
                        host=srv["pg"]["host"],
                        database=srv["pg"]["database"],
                        user=srv["pg"]["user"],
                        password=srv["pg"]["password"],
                        port=srv["pg"]["port"],
                        connect_timeout=2,
                    )

                    test_p.close()

                    st.success(
                        f"PostgreSQL Online: "
                        f"{srv['pg']['host']}:{srv['pg']['port']}"
                    )

                except Exception as e:
                    st.error(f"PostgreSQL Offline: {e}")

            # MongoDB health check
            with col_b:
                try:
                    test_m = MongoClient(
                        srv["mongo"]["uri"],
                        serverSelectionTimeoutMS=2000
                    )

                    test_m.admin.command("ping")
                    test_m.close()

                    st.success(
                        f"MongoDB Online: "
                        f"{srv['mongo']['database']}"
                    )

                except Exception as e:
                    st.error(f"MongoDB Offline: {e}")

            with col_c:
                st.markdown(
                    f"[Switch to this Server](?server={srv_id})"
                )

# --- TAB 6: PERFORMANCE MONITORING ---

with tab6:
    st.subheader(
        f"Database Performance Monitoring - {active_server['name']}"
    )

    st.markdown(
        "Monitor PostgreSQL slow queries, deadlocks, "
        "execution times and active connections."
    )

    if st.button("Refresh Performance Data", key="refresh_performance"):
        st.rerun()

    if pg_conn is not None:
        df_slow = fetch_slow_queries(pg_conn)
        df_historical = fetch_historical_slow_queries(pg_conn)
        df_deadlocks = fetch_deadlock_stats(pg_conn)
        df_connections = fetch_connection_stats(pg_conn)

        # PERFORMANCE HISTORY TRACKING
        if "performance_history" not in st.session_state:
            st.session_state["performance_history"] = []

        current_deadlocks = 0

        if not df_deadlocks.empty:
            current_deadlocks = int(
                df_deadlocks.iloc[0]["deadlocks"]
            )

        performance_snapshot = {
            "Time": datetime.now(),
            "Slow Queries": len(df_slow),
            "Deadlocks": current_deadlocks,
        }

        st.session_state["performance_history"].append(
            performance_snapshot
        )

        # Keep only the latest 60 snapshots
        st.session_state["performance_history"] = (
            st.session_state["performance_history"][-60:]
        )

        # CONNECTION METRICS
        st.markdown("---")
        st.markdown("### Database Connection Statistics")

        if not df_connections.empty:
            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Connections",
                int(df_connections.iloc[0]["total_connections"])
            )

            col2.metric(
                "Active Connections",
                int(df_connections.iloc[0]["active_connections"])
            )

            col3.metric(
                "Idle Connections",
                int(df_connections.iloc[0]["idle_connections"])
            )

        # SLOW QUERIES
        st.markdown("---")
        st.markdown("### Slow Query Monitoring")

        st.caption(
            "Currently executing SQL queries running longer than 2 seconds."
        )

        if not df_slow.empty:
            st.warning(
                f"{len(df_slow)} slow queries detected!"
            )

            st.dataframe(
                df_slow,
                width="stretch"
            )
        else:
            st.success("No slow queries detected currently.")

        # HISTORICAL QUERIES
        st.markdown("---")
        st.markdown("### Historical Slow Query Analysis")

        if not df_historical.empty:
            st.dataframe(
                df_historical,
                width="stretch"
            )

            st.markdown("### Average Query Execution Time (ms)")

            chart_data = df_historical[
                ["query", "avg_time_ms"]
            ].copy()

            chart_data["query"] = (
                chart_data["query"].str.slice(0, 50)
            )

            chart_data = chart_data.set_index("query")

            st.bar_chart(
                chart_data,
                width="stretch"
            )
        else:
            st.info(
                "Historical statistics unavailable. "
                "Enable pg_stat_statements on this server."
            )

        # DEADLOCK MONITORING
        st.markdown("---")
        st.markdown("### Deadlock Detection")

        if not df_deadlocks.empty:
            deadlock_count = int(
                df_deadlocks.iloc[0]["deadlocks"]
            )

            col1, col2 = st.columns(2)

            col1.metric(
                "Total Deadlocks",
                deadlock_count
            )

            col2.metric(
                "Statistics Reset",
                str(df_deadlocks.iloc[0]["stats_reset"])
            )

            if deadlock_count > 0:
                st.error(
                    f"{deadlock_count} deadlock(s) recorded "
                    "since the last statistics reset."
                )
            else:
                st.success(
                    "No deadlocks recorded since statistics reset."
                )

        # LIVE PERFORMANCE LINE GRAPH
        st.markdown("---")
        st.markdown("### Live Database Performance Trends")

        st.caption(
            "Tracking slow queries and PostgreSQL deadlocks "
            "across recent dashboard refreshes."
        )

        df_performance_history = pd.DataFrame(
            st.session_state["performance_history"]
        )

        if not df_performance_history.empty:
            df_performance_history = (
                df_performance_history.set_index("Time")
            )

            st.line_chart(
                df_performance_history[
                    ["Slow Queries", "Deadlocks"]
                ],
                height=350,
                width="stretch",
            )

            st.markdown("### Performance History")

            st.dataframe(
                df_performance_history,
                width="stretch"
            )
        else:
            st.info("Waiting for performance monitoring data.")

        # PERFORMANCE SUMMARY
        st.markdown("---")
        st.markdown("### Performance Summary")

        col1, col2 = st.columns(2)

        col1.metric(
            "Currently Running Slow Queries",
            len(df_slow)
        )

        if not df_historical.empty:
            slowest_time = df_historical["avg_time_ms"].max()

            col2.metric(
                "Highest Average Query Time",
                f"{slowest_time:.2f} ms"
            )
        else:
            col2.metric(
                "Historical Query Data",
                "Unavailable"
            )

    else:
        st.error(
            "PostgreSQL connection unavailable. "
            "Performance monitoring cannot be displayed."
        )
