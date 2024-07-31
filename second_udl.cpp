#include <memory>
#include <map>
#include <iostream>
#include <unordered_map>
#include <cascade/user_defined_logic_interface.hpp>
#include <cascade/utils.hpp>
#include <cascade/cascade_interface.hpp>



namespace derecho{
namespace cascade{

#define MY_UUID     "11a2c123-2200-21ac-1755-0002ac220000"
#define MY_DESC     "UDL search among the centroids to find the top num_centroids that the queries close to."


std::string get_uuid() {
    return MY_UUID;
}

std::string get_description() {
    return MY_DESC;
}

class SecondOCDPO: public DefaultOffCriticalDataPathObserver {

    int my_id = -1; // id of this node; logging purpose

    


    virtual void ocdpo_handler(const node_id_t sender,
                               const std::string& object_pool_pathname,
                               const std::string& key_string,
                               const ObjectWithStringKey& object,
                               const emit_func_t& emit,
                               DefaultCascadeContextType* typed_ctxt,
                               uint32_t worker_id) override {
          /*** Note: this object_pool_pathname is trigger pathname prefix: /rag/emb/centroids_search instead of /rag/emb, i.e. the objp name***/
          dbg_default_debug("[Cluster search ocdpo]: I({}) received an object from sender:{} with key={}", worker_id, sender, key_string);
          int client_id = 0;
          int query_batch_id = std::stoi(key_string);
          TimestampLogger::log(LOG_CLUSTER_SEARCH_UDL_START,this->my_id,query_batch_id,0);
          
          

          Blob blob(reinterpret_cast<const uint8_t*>(object.blob.bytes), object.blob.size, true);
          std::string new_key = key_string + "_result/0";
          emit(new_key, EMIT_NO_VERSION_AND_TIMESTAMP , blob);

          dbg_default_debug("[Cluster search ocdpo]: Emitted key: {}",new_key);
     }
    

    static std::shared_ptr<OffCriticalDataPathObserver> ocdpo_ptr;
public:

    static void initialize() {
        if(!ocdpo_ptr) {
            ocdpo_ptr = std::make_shared<SecondOCDPO>();
        }
    }
    static auto get() {
        return ocdpo_ptr;
    }

    void set_config(DefaultCascadeContextType* typed_ctxt, const nlohmann::json& config){
        this->my_id = typed_ctxt->get_service_client_ref().get_my_id();
    }
};

std::shared_ptr<OffCriticalDataPathObserver> SecondOCDPO::ocdpo_ptr;

void initialize(ICascadeContext* ctxt) {
    SecondOCDPO::initialize();
}

std::shared_ptr<OffCriticalDataPathObserver> get_observer(
        ICascadeContext* ctxt,const nlohmann::json& config) {
    auto typed_ctxt = dynamic_cast<DefaultCascadeContextType*>(ctxt);
    std::static_pointer_cast<SecondOCDPO>(SecondOCDPO::get())->set_config(typed_ctxt,config);
    return SecondOCDPO::get();
}

void release(ICascadeContext* ctxt) {
    // nothing to release
    return;
}

} // namespace cascade
} // namespace derecho
