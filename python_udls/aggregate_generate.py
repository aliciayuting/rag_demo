#!/usr/bin/env python3
import cascade_context
from derecho.cascade.member_client import ServiceClientAPI
from derecho.cascade.member_client import TimestampLogger
from derecho.cascade.udl import UserDefinedLogic
from collections import defaultdict
import heapq
import io
import numpy as np
import json
import pickle
import re
import time
from logging_tags import *
import torch
from collections import OrderedDict
import logging
logging.basicConfig(level=logging.ERROR)
# if INCLUDE_RUNNING_LLM == 1:
#      import transformers



# Class to store the cluster search results for each query
class ClusterSearchResults:
     def __init__(self, cluster_counts, top_k, query_text):
          '''
          Constructor
          @param cluster_counts: the total number of clusters this query is searching
          @param top_k: the number of top results to return
          '''
          self.cluster_counts = cluster_counts  
          self.top_k = top_k
          # formated as {cluster0:{"emb_id1": distance1, ...}, cluster1:{"emb_id1": distance1, ...}, ...}
          self.cluster_results = {}
          self.collected_all_results = False  # true if all the selected clusters results are collected
          # formated as [(distance0, cluster_id0, emb_id0), ...]
          self.agg_top_k_res = None 
          self.query_text = query_text
          
     def select_top_k(self):
          '''
          Select the top top_k results from all cluster results
          @return a list of top_k cluster_id and emb_id, ordered from closest to farthest
          '''
          # min heap to store the top_k results TODO: double check this
          all_results = []
          for cluster_id, embeddings in self.cluster_results.items():
               for emb_id, distance in embeddings.items():
                    all_results.append((float(distance), int(cluster_id), int(emb_id)))
          top_k_results = heapq.nsmallest(self.top_k, all_results, key=lambda x: x[0])
          return top_k_results


     def add_cluster_result(self, cluster_id, cluster_search_results):
          '''
          @param cluster_search_results: the search results for this cluster. 
                                        It is a dictionary in this format{emb_id:"distance"}
          '''
          # 0. remove the item with "query_text" in the cluster_search_results:
          if "query_text" in cluster_search_results:
               del cluster_search_results["query_text"]
          # 1. add the cluster search results to the cluster_results
          if cluster_id in self.cluster_results:
               logging.error(f"[AggregateGenerateUDL] add_cluster_result: cluster_id {cluster_id} already in ClusterSearchResults")
          self.cluster_results[cluster_id] = cluster_search_results
          if len(self.cluster_results) == self.cluster_counts:
               self.agg_top_k_res = self.select_top_k()
               self.collected_all_results = True
               

# TODO: this implementation has a lot of copies for small objects (query results), 
#       could be optimized if implemented in C++. But may not be the bottleneck
class AggregateGenerateUDL(UserDefinedLogic):
     def load_llm(self,):
          model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
          self.pipeline = transformers.pipeline(
               "text-generation",
               model=model_id,
               model_kwargs={"torch_dtype": torch.bfloat16},
               device_map="auto",
          )
          self.terminators = [
               self.pipeline.tokenizer.eos_token_id,
               self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
          ]
          

     def __init__(self,conf_str):
          '''
          Constructor
          '''
          # collect the cluster search result {query_text: ClusterSearchResults, ...}
          self.cluster_search_res = {}
          self.conf = json.loads(conf_str)
          self.top_k = int(self.conf["top_k"])
          self.top_num_centroids = int(self.conf["top_num_centroids"])
          self.include_llm = int(self.conf["include_llm"])
          self.capi = ServiceClientAPI()
          self.my_id = self.capi.get_my_id()
          self.tl = TimestampLogger()
          # docs parameters
          self.doc_file_name = './perf_test/perf_data/miniset/doc_list.pickle'
          self.answer_mapping_file = './perf_test/perf_data/miniset/answer_mapping.pickle'
          self.doc_list = None
          self.answer_mapping = None
          # LLM parameters
          if self.include_llm == 1:
               self.pipeline = None
               self.terminators = None
               self.load_llm()
          
     
     
     def _get_doc(self, cluster_id, ebd_id):
          """Helper method to get a piece of document in natural language.
          @input cluster_id: The id of the KNN cluster where the document falls in.
          @input ebd_id: The id of the document within the cluster.
          @return: The document string in natural language.
          """
          if self.answer_mapping is None:
               self.tl.log(LOG_TAG_AGG_UDL_LOAD_ANSWER_START, self.my_id, 0, cluster_id)
               with open(self.answer_mapping_file, "rb") as file:
                    self.answer_mapping = pickle.load(file)
               self.tl.log(LOG_TAG_AGG_UDL_LOAD_ANSWER_END, self.my_id, 0, cluster_id)
          if self.doc_list is None:
               self.tl.log(LOG_TAG_AGG_UDL_LOAD_DOC_START, self.my_id, 0, cluster_id)
               with open(self.doc_file_name, 'rb') as file:
                    self.doc_list = pickle.load(file)
               self.tl.log(LOG_TAG_AGG_UDL_LOAD_DOC_END, self.my_id, 0, cluster_id)
          return self.doc_list[self.answer_mapping[cluster_id][ebd_id]]
          

     def retrieve_documents(self, cluster_search_res):
          """
          @input agg_top_k_res 
          [(distance0, cluster_id0, emb_id0), ...]
          @return a list that containing documents' contents, in natural language
          [document_1, document_2, ...]
          """     

          doc_list = [None] * len(cluster_search_res.agg_top_k_res)
          for idx, doc in enumerate(cluster_search_res.agg_top_k_res):
               doc_list[idx] = self._get_doc(doc[1], doc[2])
          return doc_list


     def llm_generate(self, query , docs):
          """
          @input query: query in text natural language
          @input docs: a list of documents in natural language
          @return llm_result: LLM gen answers
          """    
          query_llm_response = {}
          messages = [
               {"role": "system", "content": "Answer the user query based on this list of documents:"+" ".join(query_doc_dict["docs"])},
               {"role": "user", "content": query_doc_dict["query_text"]},
          ]
          
          tmp_res = self.pipeline(
               messages,
               max_new_tokens=256,
               eos_token_id=self.terminators,
               do_sample=True,
               temperature=0.6,
               top_p=0.9,
          )
          raw_text = tmp_res[0]["generated_text"][-1]['content']
          query_text = query_doc_dict["query_text"]
          logging.debug(f"for query:{query_text}")
          logging.debug(f"the llm generated response: {raw_text}")   
          return raw_text
          
     
     def ocdpo_handler(self,**kwargs):
          key = kwargs["key"]
          blob = kwargs["blob"]
          pathname = kwargs["pathname"]

          pos = key.find("_cluster")
          key_with_runtime_info = key[pos:]
          match = re.match(r"_cluster(\d+)_qid([0-9a-fA-F]+)", key_with_runtime_info)
          if not match:
               # This also shouldn't happen becuase the format is done by encode_centroids_search_udl, and clusters_search_udl implemented by us
               logging.error(f"[AggregateGenerate] received an object (key:{key}) with invalid key format")
               return
          cluster_id = int(match.group(1))
          qid = int(match.group(2),16) % 100000 # TODO: temp fix for qid by only using the last 5 digits

          usable_logging_key = True
          key_without_runtime_info = key[:pos]
          match = re.match(r"client(\d+)qb([0-9a-fA-F]+)", key_without_runtime_info)
          if not match:
               usable_logging_key = False  
               logging.error(f"[AggregateGenerate] received an object (key:{key}) with invalid key format that is not usable for logging purpose")
          else:
               client_id = int(match.group(1))
               batch_id = int(match.group(2))
               query_batch_id = batch_id * 100000 + qid
          if usable_logging_key:
               self.tl.log(LOG_TAG_AGG_UDL_START,self.my_id, query_batch_id, cluster_id)

          # 1. parse the blob to dict
          bytes_obj = blob.tobytes()
          json_str_decoded = bytes_obj.decode('utf-8')
          cluster_result = json.loads(json_str_decoded)
          query_text = cluster_result["query_text"]
          
          if usable_logging_key:
               self.tl.log(LOG_TAG_AGG_UDL_FINISHED_PARSE, client_id, query_batch_id, cluster_id)

          # 2. add the cluster result to the aggregated query results
          if query_text not in self.cluster_search_res:
               self.cluster_search_res[query_text] = \
                    ClusterSearchResults(self.top_num_centroids, self.top_k, query_text)

          self.cluster_search_res[query_text].add_cluster_result(cluster_id, cluster_result)
          if not self.cluster_search_res[query_text].collected_all_results:
               if usable_logging_key:
                    self.tl.log(LOG_TAG_AGG_UDL_END_NOT_FULLY_GATHERED, client_id, query_batch_id, cluster_id)
               return

          # 3.1 if collected all result, retrieve documents and run llm
          next_key = "/rag/generate/" + key_without_runtime_info + "_result/" + "qid" + str(qid) 

          if usable_logging_key:
               self.tl.log(LOG_TAG_AGG_UDL_RETRIEVE_DOC_START, client_id, query_batch_id, qid)
          doc_list = self.retrieve_documents(self.cluster_search_res[query_text])
          if usable_logging_key:
               self.tl.log(LOG_TAG_AGG_UDL_RETRIEVE_DOC_END, client_id, query_batch_id, qid)
          if self.include_llm == 1:
               llm_result = self.llm_generate(sorted_client_query_batch_result)
               final_result_dict = {"query_text": query_text, "llm_result": llm_result}
               final_result_json = json.dumps(final_result_dict)
          else:
               final_result_dict = {"query_text": query_text, "docs": doc_list}
               final_result_json = json.dumps(final_result_dict)
          # 3.2 save the result as KV object in cascade to be retrieved by client
          if usable_logging_key:
               self.tl.log(LOG_TAG_AGG_UDL_PUT_RESULT_START, client_id, query_batch_id, qid)
          self.capi.put(next_key, final_result_json.encode('utf-8'))
          logging.debug(f"[AggregateGenerate] put the agg_results to key:{next_key},\
                         \n                   value: {final_result_json}")
          if usable_logging_key:
               self.tl.log(LOG_TAG_AGG_UDL_PUT_RESULT_END, client_id, query_batch_id, qid)
          

     def __del__(self):
          pass