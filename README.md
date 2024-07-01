# rag_demo

## Requirement
1. FAISS : https://github.com/facebookresearch/faiss/blob/main/INSTALL.md 

   NVIDIA toolkit nvcc if run with GPU support

   Python support needs to be built for Python centroids_search_udl
2. cascade : https://github.com/Derecho-Project/cascade/tree/7647a5f7c55aaed9327b62bc6bac93e1cbfb1223
3. cascade Python API : https://github.com/Derecho-Project/cascade/tree/7647a5f7c55aaed9327b62bc6bac93e1cbfb1223/src/service/python
4. model dependencies:

   BGE-M3: https://github.com/FlagOpen/FlagEmbedding 

   Generator model

## Branches
This is a correctness testing branch

# Run
## Servers Commands
n0 - n3 are server nodes

n4, n5, n6 are client nodes

## Client Commands
1. create object pools
2. put embeddings
3. run UDLs


## Data Storage configuration
- embeddings: stored in /rag/emb object pool

centroids stored in the format of /rag/emb/centroids/[obj_id], e.g. /rag/emb/centroids/1, /rag/emb/centroids/2

cluster embeddings stored in the format of /rag/emb/cluster[cluster_id]/[obj_id], e.g. /rag/emb/cluster1/0, /rag/emb/cluster2/0


# Docker image
We have built a docker image that have nvcc and cascade,derecho built setup. You can pull from the docker image and run it on your environment.

Image name: yy354/rag_dev:v1.0