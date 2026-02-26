from mcp.server.fastmcp import FastMCP 

# couchbase sdk classes to connect to the database. 
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator

from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

auth = PasswordAuthenticator(
    os.getenv("CB_USERNAME"),
    os.getenv("CB_PASSWORD")
) # CReating login credentials

cluster = Cluster(
    os.getenv("CB_CONNECTION_STRING"),
    ClusterOptions(auth)
)

cluster.wait_until_ready(timeout=timedelta(seconds=5))
bucket = cluster.bucket(os.getenv("CB_BUCKET_NAME"))

mcp = FastMCP("couchbase-server") # starting server

@mcp.tool()
def query_database(sql : str) -> str:
    
    try: 
        result = cluster.query(sql)
        rows = []
        for row in result:
            rows.append(row)

        return str(rows)
    
    except Exception as e:
        return f"error : {str(e)}"


@mcp.tool()
def list_collections() -> str:
    try:
        # scope = bucket.scope("inventory") # cluster -> bucket -> scope -> collection -> documents is the CB storage order
        # scope => limits to just the inventory scope. !scope -> lists all collections in the bucket.   
        result = cluster.query(
            "SELECT RAW name FROM system:keyspaces WHERE `bucket` = 'travel-sample'"
        )
        collections = []
        for row in result:
            collections.append(row)
        
        return str(collections)
    except Exception as e:
        return f"error : {str(e)}"


if __name__ == "__main__": # ie. run this code only if the file is exec directly ( in which case name == main will match. if imported name will be = filename )
    mcp.run(transport="stdio") # std input/output for comms ( instead of HTTP )