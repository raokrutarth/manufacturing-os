
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
    BatchDeliveryConfirmResponse_received  50.00  122.00  80.75  75.50  36.53   1334.25
    BatchDeliveryConfirmResponse_sent      53.00  122.00  85.75  84.00  31.47    990.25
    BatchRequest_received                  74.00  355.00 189.50 164.50 119.36  14247.00
    BatchRequest_sent                     146.00  258.00 206.25 210.50  46.29   2142.92
    BatchSentResponse_received             54.00  123.00  86.75  85.00  31.47    990.25
    BatchSentResponse_sent                 51.00  145.00  92.50  87.00  48.27   2329.67
    BatchUnavailableResponse_received     101.00  154.00 128.33 130.00  26.54    704.33
    BatchUnavailableResponse_sent          23.00  233.00 129.33 132.00 105.03  11030.33
    HeartbeatReq_received                  58.00  148.00 111.20 117.00  32.69   1068.70
    HeartbeatReq_sent                      59.00  176.00 117.00 116.00  41.38   1712.00
    HeartbeatResp_received                 49.00  147.00 104.60 107.00  35.37   1250.80
    HeartbeatResp_sent                     58.00  148.00 111.20 117.00  32.69   1068.70
    WaitingForBatchResponse_received       49.00  124.00  81.25  76.00  37.29   1390.92
    WaitingForBatchResponse_sent           53.00  123.00  86.50  85.00  31.82   1012.33
    batch_unavailable_messages_received   101.00  154.00 128.33 130.00  26.54    704.33
    batch_unavailable_messages_sent         0.00  233.00  48.50   0.00  87.36   7632.00
    batches_consumed_total                  0.00  123.00  42.75  26.00  50.29   2528.79
    batches_delivered                       0.00  122.00  40.38  25.00  49.34   2434.84
    batches_produced_total                  0.00  274.00  70.75  51.00  92.47   8550.50
    batches_received                       53.00  122.00  85.75  84.00  31.47    990.25
    batches_requested                     145.00  258.00 206.00 210.50  46.73   2183.33
    bootstrap_all_paths_time_sec            0.00    0.00   0.00   0.00   0.00      0.00
    crash_signals_sent                      0.00    0.00   0.00   0.00    NaN       NaN
    empty_inbound_inventory_occurrences     0.00  257.00 103.00  73.00 114.14  13028.29
    empty_outbound_inventory_occurrences    0.00  233.00  48.50   0.00  87.36   7632.00
    failed_flow_queries                     0.00    0.00   0.00   0.00   0.00      0.00
    failed_flow_update                      0.00    0.00   0.00   0.00   0.00      0.00
    flow_queries                          269.00  623.00 367.12 310.00 126.21  15928.70
    full_flow_bootstrap_time_sec            0.00    0.01   0.00   0.00   0.00      0.00
    heartbeats_sent                        59.00  177.00 117.20 116.00  41.73   1741.70
    inbound_wal_size                        0.00  242.00  88.75 103.00  85.77   7355.93
    nodes_determined_crashed                0.00    0.00   0.00   0.00   0.00      0.00
    op_generator_cycles                   248.00  248.00 248.00 248.00    NaN       NaN
    outbound_material_buildup               0.00  129.00  24.62   0.50  45.64   2082.84
    outbound_wal_size                       0.00  272.00  70.38  51.00  91.76   8419.98
    received_messages                       0.00  976.00 402.25 492.50 366.77 134521.93
    recover_signals_sent                    0.00    0.00   0.00   0.00    NaN       NaN
    sent_messages                           0.00 1068.00 426.38 454.50 414.37 171698.55
    skipped_manufacture_cycles              0.00  275.00 201.25 218.00  93.01   8650.50
    successful_manufacture_cycles           0.00  275.00  70.88  51.50  92.68   8588.70
    total_manufacture_cycles              265.00  276.00 271.88 272.50   4.39     19.27
    unanswered_batch_requests_current       0.00   35.00  11.88   2.00  15.82    250.41
    wal_ghost_inbound_batches               0.00    0.00   0.00   0.00   0.00      0.00
    wal_ghost_outbound_batches              0.00    0.00   0.00   0.00   0.00      0.00
    wal_recovered_inbound_batches           0.00    0.00   0.00   0.00   0.00      0.00
    wal_recovered_outbound_batches          0.00    0.00   0.00   0.00   0.00      0.00
     ```
  
- med-no-fail `--num_types 8 --nodes_per_type 2 --failure_rate 0 --recover_rate 0`

    ```csv 
    ```

- large-no-fail `--num_types 20 --nodes_per_type 2 --failure_rate 0 --recover_rate 0`

    ```csv 
    ```




- small-low-failure `--num_types 5 --nodes_per_type 2 --failure_rate 1 --recover_rate 1`

    ```csv                                      
                                             min    max   mean median    std       var
    metric_name                                                                       
    BatchDeliveryConfirmResponse_received  21.00  77.00  44.25  39.50  27.51    756.92
    BatchDeliveryConfirmResponse_sent      22.00  77.00  47.25  45.00  22.66    513.58
    BatchRequest_received                  67.00 393.00 176.75 123.50 148.99  22197.58
    BatchRequest_sent                      91.00 278.00 193.50 202.50  79.02   6244.33
    BatchSentResponse_received             22.00  78.00  47.50  45.00  23.10    533.67
    BatchSentResponse_sent                 21.00  90.00  53.50  51.50  37.13   1379.00
    BatchUnavailableResponse_received       1.00 180.00 121.50 152.50  81.50   6641.67
    BatchUnavailableResponse_sent           1.00 312.00 123.25  90.00 137.64  18944.25
    HeartbeatReq_received                  37.00 129.00  85.20  93.00  35.07   1230.20
    HeartbeatReq_sent                      37.00 118.00  93.40 108.00  33.69   1134.80
    HeartbeatResp_received                 31.00 108.00  81.80  85.00  30.36    921.70
    HeartbeatResp_sent                     37.00 129.00  85.20  93.00  35.07   1230.20
    InformLeaderOfDeathReq_received        54.00  54.00  54.00  54.00    NaN       NaN
    InformLeaderOfDeathReq_sent             1.00  19.00  10.80  10.00   7.73     59.70
    WaitingForBatchResponse_received       21.00  78.00  45.00  40.50  28.23    796.67
    WaitingForBatchResponse_sent           22.00  78.00  47.50  45.00  23.10    533.67
    batch_unavailable_messages_received     1.00 180.00 121.25 152.00  81.39   6624.92
    batch_unavailable_messages_sent         0.00 311.00  61.50   0.50 111.30  12387.71
    batches_consumed_total                  0.00  75.00  22.88  10.50  28.46    809.84
    batches_delivered                       0.00  77.00  22.25  10.50  29.90    893.93
    batches_produced_total                  0.00 117.00  34.50  21.00  41.85   1751.14
    batches_received                       21.00  76.00  46.50  44.50  22.61    511.00
    batches_requested                      91.00 278.00 193.50 202.50  79.02   6244.33
    bootstrap_all_paths_time_sec            0.00   0.00   0.00   0.00   0.00      0.00
    crash_signals_sent                      6.00   6.00   6.00   6.00    NaN       NaN
    empty_inbound_inventory_occurrences     0.00 278.00  96.75  45.50 115.65  13373.93
    empty_outbound_inventory_occurrences    0.00 312.00  61.62   0.50 111.62  12459.12
    failed_flow_queries                     0.00   0.00   0.00   0.00   0.00      0.00
    failed_flow_update                      0.00  53.00   6.62   0.00  18.74    351.12
    flow_queries                          113.00 561.00 301.75 269.00 127.50  16257.36
    full_flow_bootstrap_time_sec            0.00   0.01   0.01   0.01   0.00      0.00
    heartbeats_sent                        37.00 118.00  93.40 108.00  33.69   1134.80
    inbound_wal_size                        0.00 150.00  48.88  42.50  52.60   2767.27
    nodes_determined_crashed                0.00   0.00   0.00   0.00   0.00      0.00
    op_generator_cycles                   288.00 288.00 288.00 288.00    NaN       NaN
    outbound_material_buildup               0.00  79.00  15.62   1.00  27.42    751.70
    outbound_wal_size                       0.00 168.00  41.50  21.00  57.67   3326.00
    received_messages                       0.00 800.00 328.88 397.50 302.61  91571.84
    recover_signals_sent                    4.00   4.00   4.00   4.00    NaN       NaN
    sent_messages                           0.00 881.00 351.00 360.00 349.06 121842.29
    skipped_manufacture_cycles              0.00 269.00 171.62 202.50  95.03   9031.41
    successful_manufacture_cycles           0.00 170.00  41.75  21.00  58.30   3398.79
    total_manufacture_cycles              115.00 271.00 214.25 226.00  58.93   3472.79
    unanswered_batch_requests_current       0.00  55.00  12.62   6.00  18.91    357.70
    wal_ghost_inbound_batches               0.00  36.00   8.50   0.00  15.78    248.86
    wal_ghost_outbound_batches              0.00   0.00   0.00   0.00   0.00      0.00
    wal_recovered_inbound_batches           0.00  35.00   4.38   0.00  12.37    153.12
    wal_recovered_outbound_batches          0.00  83.00  14.38   0.00  29.90    894.27
     ```


