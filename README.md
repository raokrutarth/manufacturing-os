
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

- small-no-fail

    ```csv                                      
                                             min     max   mean median    std       var
    metric_name                                                                        
    BatchDeliveryConfirmResponse_received  56.00  122.00  86.50  84.00  33.44   1118.33
    BatchDeliveryConfirmResponse_sent      57.00  122.00  89.75  90.00  34.50   1190.25
    BatchRequest_received                  86.00  362.00 185.50 147.00 121.35  14726.33
    BatchRequest_sent                     138.00  243.00 196.50 202.50  43.52   1893.67
    BatchSentResponse_received             58.00  123.00  90.25  90.00  34.50   1190.25
    BatchSentResponse_sent                 57.00  138.00  93.75  90.00  41.87   1752.92
    BatchUnavailableResponse_received     116.00  125.00 120.67 121.00   4.51     20.33
    BatchUnavailableResponse_sent          29.00  240.00 122.00  97.00 107.70  11599.00
    HeartbeatReq_received                  96.00  264.00 188.00 193.00  59.85   3582.50
    HeartbeatReq_sent                      98.00  288.00 194.60 196.00  67.19   4514.80
    HeartbeatResp_received                 88.00  258.00 181.80 186.00  60.82   3699.20
    HeartbeatResp_sent                     96.00  264.00 188.40 194.00  59.91   3588.80
    WaitingForBatchResponse_received       57.00  123.00  87.00  84.00  33.50   1122.00
    WaitingForBatchResponse_sent           58.00  123.00  90.25  90.00  34.50   1190.25
    batch_unavailable_messages_received   117.00  126.00 121.33 121.00   4.51     20.33
    batch_unavailable_messages_sent         0.00  241.00  45.88   0.00  85.77   7356.41
    batches_consumed_total                  0.00  121.00  44.12  28.50  51.86   2689.55
    batches_delivered                       0.00  122.00  43.25  28.00  51.16   2617.07
    batches_produced_total                 56.00  270.00 171.62 194.50 106.10  11257.12
    batches_received                       57.00  122.00  89.75  90.00  34.50   1190.25
    batches_requested                     138.00  243.00 196.50 202.50  43.52   1893.67
    bootstrap_all_paths_time_sec            0.00    0.00   0.00   0.00   0.00      0.00
    empty_inbound_inventory_occurrences     0.00  243.00  98.25  69.00 108.83  11843.64
    empty_outbound_inventory_occurrences    0.00  241.00  45.88   0.00  85.77   7356.41
    failed_flow_queries                     0.00    0.00   0.00   0.00   0.00      0.00
    flow_queries                          261.00  622.00 358.50 310.00 124.35  15463.14
    full_flow_bootstrap_time_sec            0.01    0.01   0.01   0.01   0.00      0.00
    heartbeats_sent                        98.00  287.00 194.60 196.00  66.85   4468.80
    inbound_wal_size                        0.00  243.00  92.00 116.00  86.54   7489.14
    nodes_determined_crashed                0.00    0.00   0.00   0.00   0.00      0.00
    outbound_material_buildup               0.00  270.00 124.62  93.00 127.29  16202.27
    outbound_wal_size                      56.00  270.00 171.25 193.00 105.71  11175.64
    received_messages                       0.00 1223.00 501.50 600.00 458.56 210275.43
    sent_messages                           0.00 1294.00 519.88 563.50 502.25 252253.84
    skipped_manufacture_cycles              0.00  205.00  93.25  69.00 101.93  10388.79
    successful_manufacture_cycles          57.00  271.00 172.25 195.00 106.47  11335.64
    total_manufacture_cycles              260.00  271.00 265.50 265.50   4.90     24.00
    unanswered_batch_requests_current       0.00   27.00   7.62   0.00  10.98    120.55
    wal_ghost_inbound_batches               0.00    0.00   0.00   0.00   0.00      0.00
    wal_ghost_outbound_batches              0.00    0.00   0.00   0.00   0.00      0.00
    wal_recovered_inbound_batches           0.00    0.00   0.00   0.00   0.00      0.00
    wal_recovered_outbound_batches          0.00    0.00   0.00   0.00   0.00      0.00   
     ```
  
- small-no-fail

    ```csv 
    
    ```
