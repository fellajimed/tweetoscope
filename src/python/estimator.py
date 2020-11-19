## This function estimates the parameters (p, beta) of the generating process for the cascade.
## We use the MAP estimator.

from utils import *
from json import dumps
import configparser

## read config file
config = configparser.ConfigParser(strict=False)
## the script is executed from the folder "src"
config.read('./configs/collector.ini')

<<<<<<< HEAD
=======
# def neg_power_law(alpha, mu, size=1):
#     """
#     Returns a 1D-array of samples drawn from a negative power law distribution
    
#     alpha -- power parameter of the power-law mark distribution
#     mu    -- min value parameter of the power-law mark distribution
#     size  -- number of samples
#     """
    
#     u = np.random.uniform(size=size)
#     return mu * np.exp(np.log(u) / (1. - alpha))    


# def simulate_marked_exp_hawkes_process(params, m0, alpha, mu, max_size=10000):
#     """
#     Returns a 2D-array whose rows contain marked time points simulated from an exponential Hawkes process
    
#     params   -- parameter tuple (p,beta) of the generating process
#     m0       -- magnitude of the initial tweet at t = 0.
#     alpha    -- power parameter of the power-law mark distribution
#     mu       -- min value parameter of the power-law mark distribution
#     max_size -- maximal authorized size of the cascade
#     """
    
#     p,beta = params
    
    
#     # Create an unitialized array for optimization purpose (only memory allocation)
#     T = np.empty((max_size,2))
    
#     intensity = beta * p * m0
#     t, m = 0., m0
    
#     samples = neg_power_law(alpha, mu, size=max_size)
    
#     # Main loop
#     for i in range(max_size):
#         # Save the current point before generating the next one.
#         T[i] = (t, m)
        
#         # 
#         u = np.random.uniform()
#         v = -np.log(u)
#         w = 1. - beta / intensity * v
#         # Tests if process stops generating points.
#         if w <= 0.:
#             # Shrink T to remove unused rows
#             T = T[:i,:]
#             break
            
#         # Otherwise computes the time jump dt and new time point t
#         dt = - np.log(w) / beta
#         t += dt
        
#         # And update intensity accordingly
#         m = neg_power_law(alpha, mu)
#         intensity = intensity * np.exp(-beta * dt) + beta * p * m  
#     return T

# #%%
# beta = 1/3600
# p = 0.05
# params = (p, beta)
# m0 = 1000
# alpha = 2.4
# mu = 10

# n = p*mu*(alpha-1)/(alpha-2)
# print("n*: ", n)

# cascade = simulate_marked_exp_hawkes_process(params, m0, alpha, mu, max_size=10000)


>>>>>>> added predictor and learner
## Create consumer
consumerProperties = { "bootstrap_servers":[config["kafka"]["brokers"]],
                       "auto_offset_reset":"earliest",
                       "group_id":"myOwnPrivatePythonGroup"}

consumer = KafkaConsumer(**consumerProperties)
consumer.subscribe(config["topic"]["out_series"])


## Create producer
producerProperties = {"bootstrap_servers":[config["kafka"]["brokers"]]}

producer = KafkaProducer(**producerProperties)


## Read cascades from cascade_series
for message in consumer:
   # message = key, value
   ## value.keys() = dict_keys(['key', 'source_id', 'msg', 'latest_time', 'list_retweets'])
   ## value['list_retweets'] is a list of dictionnaries => dict_keys(['time', 'magnitude', 'info'])
   key, value = msg_deserializer(message)
   cascade = np.array(value['tweets'])
   
   #estimate parameters p, beta
   estimated_params = compute_MAP(cascade)[1]
   
   #compute G1
   G1 = compute_G1(estimated_params, cascade)
   estimated_params.append(G1)

   #produce message to cascade properties
   n_obs = len(cascade)
   n_supp = estimated_size(n_obs, estimated_params)
   valeurs =  {'type': 'parameters', 'cid': value['cid'], 'msg' : value['msg'], 'n_obs': n_obs, 'n_supp' : n_supp, 'params': estimated_params.tolist()}
   producer.send(config["topic"]["out_properties"], value=msg_serializer(valeurs), key=msg_serializer(value['T_obs']))
   print(valeurs)
