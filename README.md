
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


