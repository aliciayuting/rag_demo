

EMBEDDING_DIM = 1024

'''
Configurations for offline vector database construction
'''
# NUM_CENTROIDS = 3
# NUM_EMB_PER_CENTROIDS = 10000
NUM_EMB_PER_OBJ = 200  # < 1MB/4KB = 250
USE_WHICH_FAISE_SAERCH = 0 # 0: cpu_flat, 1: gpu_flat, 2: gpu_ivf_flat, 3: gpu_ivf_pq


'''
Configuration for client side batch requests
'''
TOTAL_BATCH_COUNT = 10
QUERY_PER_BATCH = 1
MAX_RESULT_WAIT_TIME = 240 # seconds
RETRIEVE_WAIT_INTERVAL = 0.5 # seconds
PRINT_FINISH_INTEVAL = 100 # print a checkpoint after 100 batches 





'''
Parameters for generating queries in accordance with queueing theory.
'''
# Average number of queries per second, which is also the rate parameter lambda of the
# exponential distribution. This is the inverse of the scale parameter.
AVG_QUERY_PER_SEC = 10