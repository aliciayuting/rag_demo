#!/usr/bin/env python3

import json
import numpy as np
import os
import pickle
import sys
import time
from derecho.cascade.external_client import ServiceClientAPI
from derecho.cascade.external_client import TimestampLogger

from perf_config import *

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../python_udls')))
from logging_tags import *

import logging
logging.basicConfig(level=logging.ERROR)

OBJECT_POOLS_LIST = "setup/object_pools.list"


SUBGROUP_TYPES = {
        "VCSS": "VolatileCascadeStoreWithStringKey",
        "PCSS": "PersistentCascadeStoreWithStringKey",
        "TCSS": "TriggerCascadeNoStoreWithStringKey"
        }


QUERY_PICKLE_FILE = "validate_first_100_query.pickle"
script_dir = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(script_dir, "perf_data/miniset/")
query_list = None




def get_queries(basepath, filename, batch_id):
     '''
     Load the queries from pickle files
     '''
     global query_list
     if query_list is None:
          fpath = os.path.join(basepath, filename)
          with open(fpath, 'rb') as file:
               query_list = pickle.load(file)
     return query_list[QUERY_PER_BATCH * batch_id : QUERY_PER_BATCH * (batch_id + 1)]


def generate_random_embeddings(d=64, num_embs=100):
    '''
    Load the embeddings from pickle files
    '''
    xb = np.random.random((num_embs, d)).astype('float32')
    xb[:, 0] += np.arange(num_embs) / 1000.
    return xb



def main(argv):
     capi = ServiceClientAPI()
     print("Connected to Cascade service ...")
     client_id = capi.get_my_id()
     tl = TimestampLogger()

     for querybatch_id in range(TOTAL_BATCH_COUNT):
          # Send batch of queries to Cascade service
          key = f"/rag/emb/centroids_search/client{client_id}qb{querybatch_id}"
          query_list = get_queries(DATASET_PATH, QUERY_PICKLE_FILE, querybatch_id)
          query_list_json = json.dumps(query_list)
          query_list_json_bytes = query_list_json.encode('utf-8')
          emb_list = generate_random_embeddings(d=EMBEDDING_DIM, num_embs=len(query_list))
          emb_list_bytes = emb_list.tobytes()
          num_queries = len(query_list)
          num_queries_bytes = num_queries.to_bytes(4, byteorder='big', signed=False)
          # object to be put to cascade is in the formate of a byte array with 3 main parts:
          # [number of queries (4 bytes)  + query embeddings (d*number of queries bytes) + query list json (variable length)]
          encoded_bytes = num_queries_bytes + emb_list_bytes + query_list_json_bytes
          tl.log(LOG_TAG_QUERIES_SENDING_START, client_id, querybatch_id, 0)
          res = capi.put_and_forget(key, encoded_bytes)
          tl.log(LOG_TAG_QUERIES_SENDING_END, client_id, querybatch_id, 0)
          logging.debug(f"Put queries to key:{key}, batch_size:{len(query_list)}")

          # Wait for result of this batch
          result_prefix = "/rag/generate/" + f"client{client_id}qb{querybatch_id}_result"
          result_generated = False
          wait_time = 0
          retrieved_queries = set() # track the queries to be retrieved
          while not result_generated and wait_time < MAX_RESULT_WAIT_TIME:
               existing_queries = capi.list_keys_in_object_pool(result_prefix)
               new_keys_to_retrieve = [] 
               # Need to process all the futures, because embedding objects may hashed to different shards
               for r in existing_queries:
                    keys = r.get_result()
                    for key in keys:
                         if key not in retrieved_queries:
                              new_keys_to_retrieve.append(key)
               for result_key in new_keys_to_retrieve:
                    result_future = capi.get(result_key)
                    if result_future:
                         res_dict = result_future.get_result()
                         if len(res_dict['value']) > 0:
                              retrieved_queries.add(result_key)
                              qid = int(result_key.split("/")[-1][3:])
                              tl.log(LOG_TAG_QUERIES_RESULT_CLIENT_RECEIVED,client_id,querybatch_id,qid)
                              # result dictionary format["query_id": (float(distance), int(cluster_id), int(emb_id)), "query_id":(...) ... ]
                              logging.debug(f"Got result from key:{result_key}")
                    else:
                         logging.debug(f"Getting key:{result_key} with NULL result_future.")
               if num_queries == len(retrieved_queries):
                    result_generated = True
               else:
                    time.sleep(RETRIEVE_WAIT_INTERVAL)
                    wait_time += RETRIEVE_WAIT_INTERVAL
          if not result_generated:
               logging.debug(f"Failed to get result for querybatch_id:{querybatch_id} after {MAX_RESULT_WAIT_TIME} seconds.")
          if (querybatch_id + 1) % PRINT_FINISH_INTEVAL == 0:
               print(f"Finished processing query_batch {querybatch_id}")

     tl.flush(f"client_timestamp.dat")

     # notify all nodes to flush logs
     # TODO: read it from object_pool.list to send this notification to both /rag/emb and /rag/generate object pool's subgroup's shards
     subgroup_type = SUBGROUP_TYPES["VCSS"]
     subgroup_index = 0
     num_shards = len(capi.get_subgroup_members(subgroup_type,subgroup_index))
     for i in range(num_shards):
          shard_index = i
          capi.put("/rag/emb/centroids_search/flush_logs", b"",subgroup_type=subgroup_type,subgroup_index=subgroup_index,shard_index=shard_index)

     print("Done!")


if __name__ == "__main__":
     main(sys.argv)