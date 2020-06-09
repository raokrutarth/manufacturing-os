
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





