
# Distributed Manufacturing operation system

[Design Doc](https://docs.google.com/document/d/14D9z-c7i1_GU2eFmPw7M6nCwIaInTCtb14OPEwDR4mo/edit#)

## Overview

TODO

### Running Project

#### Setup

```bash
python3.5 -m pip install -r requirements.txt
```

### Execution

```bash
python3.5 src/main.py
```

### Experiments

- small-no-fail `--num_types 5 --nodes_per_type 2 --failure_rate 0 --recover_rate 0`

    ```csv                                      
                                        min    max  mean median   std     var
metric_name                                                                  
BatchDeliveryConfirmResponse_received  6.00  22.00 13.50  13.00  7.72   59.67
BatchDeliveryConfirmResponse_sent      7.00  23.00 14.25  13.50  6.70   44.92
BatchRequest_received                 15.00  68.00 37.50  33.50 22.96  527.00
BatchRequest_sent                     26.00  56.00 39.75  38.50 12.50  156.25
BatchSentResponse_received             8.00  23.00 14.75  14.00  6.24   38.92
BatchSentResponse_sent                 7.00  26.00 15.50  14.50  9.47   89.67
BatchUnavailableResponse_received     18.00  41.00 28.67  27.00 11.59  134.33
BatchUnavailableResponse_sent          7.00  46.00 29.00  34.00 19.97  399.00
HeartbeatReq_received                 11.00  27.00 20.40  21.00  5.81   33.80
HeartbeatReq_sent                     11.00  32.00 21.20  21.00  7.46   55.70
HeartbeatResp_received                 9.00  27.00 19.20  19.00  6.57   43.20
HeartbeatResp_sent                    11.00  27.00 20.20  21.00  5.76   33.20
WaitingForBatchResponse_received       7.00  23.00 14.00  13.00  7.79   60.67
WaitingForBatchResponse_sent           8.00  23.00 14.50  13.50  6.35   40.33
batch_unavailable_messages_received   18.00  41.00 28.67  27.00 11.59  134.33
batch_unavailable_messages_sent        0.00  46.00 10.88   0.00 18.42  339.27
batches_consumed_total                 0.00  22.00  6.62   3.50  8.19   67.13
batches_delivered                      0.00  22.00  6.75   3.00  8.81   77.64
batches_produced_total                 0.00  49.00 12.00   6.50 16.74  280.29
batches_received                       7.00  23.00 14.25  13.50  6.70   44.92
batches_requested                     25.00  56.00 39.50  38.50 12.87  165.67
bootstrap_all_paths_time_sec           0.00   0.00  0.00   0.00  0.00    0.00
crash_signals_sent                     0.00   0.00  0.00   0.00   NaN     NaN
empty_inbound_inventory_occurrences    0.00  56.00 19.75  13.00 22.64  512.50
empty_outbound_inventory_occurrences   0.00  46.00 10.88   0.00 18.42  339.27
failed_flow_queries                    0.00   0.00  0.00   0.00  0.00    0.00
failed_flow_update                     0.00   0.00  0.00   0.00  0.00    0.00
flow_queries                          48.00 116.00 67.00  55.50 25.22  636.29
full_flow_bootstrap_time_sec           0.00   0.01  0.01   0.01  0.00    0.00
heartbeats_sent                       11.00  33.00 21.20  20.00  7.85   61.70
inbound_wal_size                       0.00  44.00 15.00  15.00 15.36  236.00
nodes_determined_crashed               0.00   0.00  0.00   0.00  0.00    0.00
op_generator_cycles                   48.00  48.00 48.00  48.00   NaN     NaN
outbound_material_buildup              0.00  23.00  4.25   0.50  7.91   62.50
outbound_wal_size                      0.00  49.00 12.00   6.50 16.74  280.29
received_messages                      0.00 181.00 75.38  95.50 68.28 4662.27
recover_signals_sent                   0.00   0.00  0.00   0.00   NaN     NaN
sent_messages                          0.00 198.00 78.75  82.50 76.77 5893.36
skipped_manufacture_cycles             0.00  47.00 35.50  40.50 16.03  256.86
successful_manufacture_cycles          0.00  49.00 12.12   7.00 16.69  278.70
total_manufacture_cycles              47.00  50.00 48.00  48.00  0.93    0.86
unanswered_batch_requests_current      0.00   7.00  2.00   0.50  2.73    7.43
wal_ghost_inbound_batches              0.00   0.00  0.00   0.00  0.00    0.00
wal_ghost_outbound_batches             0.00   0.00  0.00   0.00  0.00    0.00
wal_recovered_inbound_batches          0.00   0.00  0.00   0.00  0.00    0.00
wal_recovered_outbound_batches         0.00   0.00  0.00   0.00  0.00    0.00
     ```
  
- med-no-fail `--num_types 8 --nodes_per_type 2 --failure_rate 0 --recover_rate 0`

    ```csv 
                                             min     max   mean median    std       var
    metric_name                                                                        
    BatchDeliveryConfirmResponse_received  12.00  111.00  45.86  28.00  38.79   1504.81
    BatchDeliveryConfirmResponse_sent      12.00  111.00  48.86  41.00  31.29    978.81
    BatchRequest_received                  71.00  399.00 236.71 231.00 113.01  12770.24
    BatchRequest_sent                     142.00  402.00 254.57 224.00  91.68   8404.62
    BatchSentResponse_received             13.00  111.00  49.00  41.00  31.02    962.33
    BatchSentResponse_sent                 13.00  142.00  53.57  28.00  51.25   2626.95
    BatchUnavailableResponse_received     104.00  316.00 214.00 213.00  89.92   8086.40
    BatchUnavailableResponse_sent          43.00  312.00 213.83 219.00  94.80   8986.17
    HeartbeatReq_received                  92.00  471.00 271.62 279.50 128.60  16536.84
    HeartbeatReq_sent                      96.00  458.00 280.00 283.00 128.42  16492.29
    HeartbeatResp_received                 78.00  440.00 261.25 274.00 122.94  15114.50
    HeartbeatResp_sent                     92.00  471.00 271.62 279.50 128.60  16537.41
    WaitingForBatchResponse_received       12.00  112.00  46.14  28.00  38.99   1520.48
    WaitingForBatchResponse_sent           13.00  112.00  49.14  41.00  31.36    983.14
    batch_unavailable_messages_received   104.00  317.00 214.33 213.00  90.37   8166.67
    batch_unavailable_messages_sent         0.00  312.00  91.79   0.00 124.70  15549.41
    batches_consumed_total                  0.00  110.00  23.79   6.00  32.47   1054.18
    batches_delivered                       0.00  111.00  22.93   6.00  35.51   1260.69
    batches_produced_total                 12.00  263.00 150.14 185.50 118.26  13984.75
    batches_received                       12.00  111.00  48.86  41.00  31.29    978.81
    batches_requested                     142.00  403.00 254.86 224.00  92.41   8540.48
    bootstrap_all_paths_time_sec            0.00    0.00   0.00   0.00   0.00      0.00
    empty_inbound_inventory_occurrences     0.00  401.00 127.29  71.00 146.01  21320.07
    empty_outbound_inventory_occurrences    0.00  312.00  91.71   0.00 124.73  15556.37
    failed_flow_queries                     0.00    0.00   0.00   0.00   0.00      0.00
    failed_flow_update                      0.00    0.00   0.00   0.00   0.00      0.00
    flow_queries                          256.00  649.00 374.57 293.50 139.40  19431.03
    full_flow_bootstrap_time_sec            0.01    0.08   0.02   0.01   0.02      0.00
    heartbeats_sent                        96.00  458.00 280.00 283.50 128.43  16494.29
    inbound_wal_size                        0.00  222.00  51.21  32.00  66.17   4378.49
    nodes_determined_crashed                0.00    0.00   0.00   0.00   0.00      0.00
    outbound_material_buildup               0.00  263.00 123.43  72.50 128.01  16387.65
    outbound_wal_size                      12.00  263.00 149.79 183.00 118.10  13946.80
    received_messages                       0.00 1524.00 585.07 484.50 599.60 359525.92
    sent_messages                           0.00 1659.00 609.00 395.50 647.51 419263.08
    skipped_manufacture_cycles              0.00  245.00 105.93  71.00 112.36  12623.92
    successful_manufacture_cycles          12.00  264.00 150.43 186.50 119.03  14169.19
    total_manufacture_cycles              237.00  264.00 255.79 259.50   8.47     71.72
    unanswered_batch_requests_current       0.00   45.00  12.14   0.50  17.60    309.82
    wal_ghost_inbound_batches               0.00    0.00   0.00   0.00   0.00      0.00
    wal_ghost_outbound_batches              0.00    0.00   0.00   0.00   0.00      0.00
    wal_recovered_inbound_batches           0.00    0.00   0.00   0.00   0.00      0.00
    wal_recovered_outbound_batches          0.00    0.00   0.00   0.00   0.00      0.00

    ```

- large-no-fail `--num_types 20 --nodes_per_type 2 --failure_rate 0 --recover_rate 0`

    ```csv 
                                           min   max  mean median  std   var
    metric_name                                                             
    batch_unavailable_messages_sent       0.00  0.00  0.00   0.00 0.00  0.00
    batches_consumed_total                0.00  0.00  0.00   0.00 0.00  0.00
    batches_delivered                     0.00  0.00  0.00   0.00 0.00  0.00
    batches_produced_total                0.00  0.00  0.00   0.00 0.00  0.00
    bootstrap_all_paths_time_sec          0.00  0.39  0.10   0.11 0.10  0.01
    empty_inbound_inventory_occurrences   0.00  0.00  0.00   0.00 0.00  0.00
    empty_outbound_inventory_occurrences  0.00  0.00  0.00   0.00 0.00  0.00
    failed_flow_queries                  71.00 91.00 75.91  74.00 6.22 38.65
    failed_flow_update                    0.00  0.00  0.00   0.00 0.00  0.00
    flow_queries                         71.00 92.00 76.33  74.00 6.36 40.48
    inbound_wal_size                      0.00  0.00  0.00   0.00 0.00  0.00
    nodes_determined_crashed              0.00  0.00  0.00   0.00 0.00  0.00
    outbound_material_buildup             0.00  0.00  0.00   0.00 0.00  0.00
    outbound_wal_size                     0.00  0.00  0.00   0.00 0.00  0.00
    received_messages                     0.00  0.00  0.00   0.00 0.00  0.00
    sent_messages                         0.00  0.00  0.00   0.00 0.00  0.00
    skipped_manufacture_cycles           71.00 91.00 75.91  74.00 6.22 38.65
    successful_manufacture_cycles         0.00  0.00  0.00   0.00 0.00  0.00
    total_manufacture_cycles             71.00 92.00 76.73  74.00 6.20 38.45
    unanswered_batch_requests_current     0.00  0.00  0.00   0.00 0.00  0.00
    wal_ghost_inbound_batches             0.00  0.00  0.00   0.00 0.00  0.00
    wal_ghost_outbound_batches            0.00  0.00  0.00   0.00 0.00  0.00
    wal_recovered_inbound_batches         0.00  0.00  0.00   0.00 0.00  0.00
    wal_recovered_outbound_batches        0.00  0.00  0.00   0.00 0.00  0.00
    ```




- small-low-failure `--num_types 5 --nodes_per_type 2 --failure_rate 1 --recover_rate 1`

    ```csv                                      
                                             min    max   mean median    std       var
    metric_name                                                                       
    BatchDeliveryConfirmResponse_received  18.00  54.00  35.50  35.00  19.14    366.33
    BatchDeliveryConfirmResponse_sent      22.00  50.00  35.50  35.00  11.70    137.00
    BatchRequest_received                  30.00 341.00 146.75 108.00 141.91  20138.92
    BatchRequest_sent                      52.00 193.00 145.50 168.50  63.40   4019.00
    BatchSentResponse_received             23.00  50.00  35.75  35.00  11.32    128.25
    BatchSentResponse_sent                 18.00  66.00  38.50  35.00  23.46    550.33
    BatchUnavailableResponse_received       4.00 155.00 105.75 132.00  68.93   4751.58
    BatchUnavailableResponse_sent           4.00 275.00 108.50  77.50 128.68  16559.00
    HeartbeatReq_received                  39.00 180.00 114.80 110.00  51.84   2687.70
    HeartbeatReq_sent                      40.00 140.00 115.00 138.00  42.91   1841.00
    HeartbeatResp_received                 40.00 139.00 112.80 132.00  41.82   1748.70
    HeartbeatResp_sent                     39.00 180.00 114.40 109.00  51.92   2695.30
    InformLeaderOfDeathReq_received        68.00  68.00  68.00  68.00    NaN       NaN
    InformLeaderOfDeathReq_sent             4.00  32.00  22.67  32.00  16.17    261.33
    WaitingForBatchResponse_received       18.00  55.00  35.75  35.00  19.47    378.92
    WaitingForBatchResponse_sent           23.00  50.00  35.75  35.00  11.32    128.25
    batch_unavailable_messages_received     4.00 155.00 106.00 132.50  69.09   4774.00
    batch_unavailable_messages_sent         0.00 275.00  54.25   2.00 102.28  10460.21
    batches_consumed_total                  0.00  36.00  11.12   0.00  16.28    264.98
    batches_delivered                       0.00  54.00  17.75   9.00  22.74    517.07
    batches_produced_total                  0.00 239.00 109.62  98.00  86.79   7531.70
    batches_received                       21.00  48.00  34.50  34.50  11.39    129.67
    batches_requested                      51.00 193.00 145.50 169.00  64.01   4097.67
    bootstrap_all_paths_time_sec            0.00   0.00   0.00   0.00   0.00      0.00
    empty_inbound_inventory_occurrences     0.00 192.00  72.88  26.00  88.27   7791.84
    empty_outbound_inventory_occurrences    0.00 276.00  54.38   2.00 102.58  10523.41
    failed_flow_queries                     0.00   0.00   0.00   0.00   0.00      0.00
    failed_flow_update                      0.00  64.00   8.00   0.00  22.63    512.00
    flow_queries                          115.00 504.00 281.75 251.50 123.58  15272.50
    full_flow_bootstrap_time_sec            0.01   0.02   0.01   0.01   0.01      0.00
    heartbeats_sent                        40.00 140.00 115.00 138.00  43.03   1852.00
    inbound_wal_size                        0.00 109.00  35.62  39.50  36.95   1365.41
    nodes_determined_crashed                0.00   0.00   0.00   0.00   0.00      0.00
    outbound_material_buildup               0.00 261.00 118.12 102.50  89.95   8091.55
    outbound_wal_size                      24.00 261.00 137.00 111.00  80.13   6421.43
    received_messages                       0.00 796.00 330.25 343.50 315.48  99529.36
    sent_messages                           0.00 793.00 333.38 326.50 334.04 111579.98
    skipped_manufacture_cycles              0.00 170.00  70.00  26.00  84.12   7075.43
    successful_manufacture_cycles          24.00 262.00 137.88 112.00  80.34   6453.84
    total_manufacture_cycles              115.00 263.00 208.75 217.50  56.26   3164.79
    unanswered_batch_requests_current       0.00  22.00   2.75   0.00   7.78     60.50
    wal_ghost_inbound_batches               0.00  35.00   8.12   0.00  15.10    228.12
    wal_ghost_outbound_batches              0.00   0.00   0.00   0.00   0.00      0.00
    wal_recovered_inbound_batches           0.00  31.00   3.88   0.00  10.96    120.12
    wal_recovered_outbound_batches          0.00 103.00  31.38  14.50  40.99   1679.98
     ```


