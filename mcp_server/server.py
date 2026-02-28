print('starting server...') # test

from mcp.server.fastmcp import FastMCP 

# couchbase sdk classes to connect to the database. 
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator

from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()


print("CONN:", os.getenv("CB_CONNECTION_STRING"))
print("USER:", os.getenv("CB_USERNAME"))
print("BUCKET:", os.getenv("CB_BUCKET_NAME"))

auth = PasswordAuthenticator(
    os.getenv("CB_USERNAME"),
    os.getenv("CB_PASSWORD")
) # CReating login credentials

cluster = Cluster(
    os.getenv("CB_CONNECTION_STRING"),
    ClusterOptions(auth)
)

# cluster.wait_until_ready(timeout=timedelta(seconds=5))
# removed wait_until_ready to prevent blocking startup. sdk connects lazily on 1st query

bucket = cluster.bucket(os.getenv("CB_BUCKET_NAME"))

mcp = FastMCP("couchbase-server") # starting server

@mcp.tool()
def query_inventory(collection: str, where: str = "", limit: int = 5) -> str:
    try:
        query = f"""
        SELECT *
        FROM `travel-sample`.`inventory`.`{collection}`
        {f"WHERE {where}" if where else ""}
        LIMIT {limit}
        """
        result = cluster.query(query)
        return str([row for row in result])
    except Exception as e:
        return f"error: {str(e)}"

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