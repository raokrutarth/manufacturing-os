
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

#### No Failures

- small-no-fail `--num_types 5 --nodes_per_type 2 --failure_rate 0 --recover_rate 0`

    ```csv
                                             min     max    mean  median     std        var
    metric_name

    BatchDeliveryConfirmResponse_received 117.00  276.00  195.75  195.00   90.94    8270.25
    BatchDeliveryConfirmResponse_sent     118.00  275.00  195.75  195.00   71.22    5071.58
    BatchRequest_received                 121.00  831.00  411.25  346.50  304.83   92920.25
    BatchRequest_sent                     276.00  538.00  411.50  416.00  108.33   11734.33
    BatchSentResponse_received            119.00  277.00  196.75  195.50   71.77    5150.92
    BatchSentResponse_sent                116.00  277.00  196.50  196.50   92.38    8533.67
    BatchUnavailableResponse_received     237.00  317.00  285.33  302.00   42.52    1808.33
    BatchUnavailableResponse_sent           4.00  556.00  286.67  300.00  276.24   76309.33
    HeartbeatReq_received                 195.00  585.00  389.80  390.00  137.89   19012.70
    HeartbeatReq_sent                     196.00  575.00  388.20  389.00  134.02   17962.70
    HeartbeatResp_received                196.00  584.00  389.60  390.00  137.18   18818.80
    HeartbeatResp_sent                    195.00  586.00  389.80  390.00  138.24   19111.20
    WaitingForBatchResponse_received      115.00  275.00  195.25  195.50   91.51    8374.92
    WaitingForBatchResponse_sent          118.00  276.00  196.25  195.50   71.76    5149.58
    batch_unavailable_messages_received   237.00  317.00  285.33  302.00   42.52    1808.33
    batch_unavailable_messages_sent         0.00  555.00  107.25    0.00  208.88   43631.64
    batches_consumed_total                  0.00  276.00   97.75   58.50  114.58   13128.21
    batches_delivered                       0.00  276.00   98.00   58.50  120.59   14542.57
    batches_produced_total                  0.00  556.00  152.75  116.50  189.15   35777.93
    batches_received                      118.00  275.00  195.75  195.00   71.22    5071.58
    batches_requested                     277.00  538.00  411.75  416.00  107.91   11644.25
    bootstrap_all_paths_time_sec            0.00    0.00    0.00    0.00    0.00       0.00
    crash_signals_sent                      0.00    0.00    0.00    0.00     NaN        NaN
    empty_inbound_inventory_occurrences     0.00  538.00  205.62  138.00  230.96   53343.98
    empty_outbound_inventory_occurrences    0.00  556.00  107.50    0.00  209.32   43814.57
    failed_flow_queries                     0.00    0.00    0.00    0.00    0.00       0.00
    failed_flow_update                      0.00    0.00    0.00    0.00    0.00       0.00
    flow_queries                          551.00 1383.00  763.62  620.00  293.12   85919.70
    full_flow_bootstrap_time_sec            0.00    0.01    0.01    0.01    0.00       0.00
    heartbeats_sent                       196.00  574.00  388.00  389.00  133.68   17869.50
    inbound_wal_size                        0.00  552.00  196.25  234.50  191.71   36753.93
    nodes_determined_crashed                0.00    0.00    0.00    0.00    0.00       0.00
    op_generator_cycles                   548.00  548.00  548.00  548.00     NaN        NaN
    outbound_material_buildup               0.00  279.00   54.38    0.00   99.46    9891.98
    outbound_wal_size                       0.00  541.00  150.88  116.50  184.60   34077.84
    received_messages                       0.00 2824.00 1093.38 1266.50 1030.11 1061117.70
    recover_signals_sent                    0.00    0.00    0.00    0.00     NaN        NaN
    sent_messages                           0.00 2819.00 1093.88 1138.50 1075.18 1156022.70
    skipped_manufacture_cycles              0.00  436.00  192.88  138.50  211.95   44924.12
    successful_manufacture_cycles           0.00  556.00  152.75  116.50  189.15   35777.93
    total_manufacture_cycles              548.00  567.00  557.62  554.50    8.07      65.13
    unanswered_batch_requests_current       0.00    2.00    0.50    0.00    0.93       0.86
    wal_ghost_inbound_batches               0.00    0.00    0.00    0.00    0.00       0.00
    wal_ghost_outbound_batches              0.00    0.00    0.00    0.00    0.00       0.00
    wal_recovered_inbound_batches           0.00    0.00    0.00    0.00    0.00       0.00
    wal_recovered_outbound_batches          0.00    0.00    0.00    0.00    0.00       0.00

     ```

- med-no-fail `--num_types 8 --nodes_per_type 2 --failure_rate 0 --recover_rate 0`

    ```csv
                                           min     max    mean  median     std        var
    metric_name
    BatchDeliveryConfirmResponse_received  18.00  274.00  111.00   41.00  115.28   13288.67
    BatchDeliveryConfirmResponse_sent      18.00  272.00  110.71   99.00   81.08    6573.24
    BatchRequest_received                  66.00  939.00  481.00  528.00  349.77  122338.00
    BatchRequest_sent                     274.00  653.00  481.43  451.00  129.71   16825.62
    BatchSentResponse_received             18.00  274.00  111.14   99.00   81.75    6683.48
    BatchSentResponse_sent                 18.00  274.00  111.29   41.00  115.74   13395.90
    BatchUnavailableResponse_received     278.00  575.00  430.83  432.50  132.50   17557.37
    BatchUnavailableResponse_sent          25.00  820.00  431.17  512.50  312.56   97695.77
    HeartbeatReq_received                 193.00  971.00  581.25  579.50  274.97   75607.93
    HeartbeatReq_sent                     197.00  950.00  579.00  583.50  268.04   71843.43
    HeartbeatResp_received                197.00  950.00  576.88  583.00  266.52   71032.70
    HeartbeatResp_sent                    193.00  970.00  580.75  579.00  274.97   75608.21
    WaitingForBatchResponse_received       18.00  274.00  111.14   41.00  115.51   13342.14
    WaitingForBatchResponse_sent           18.00  274.00  110.86   99.00   81.89    6706.14
    batch_unavailable_messages_received   278.00  575.00  430.83  432.50  132.50   17557.37
    batch_unavailable_messages_sent         0.00  820.00  184.79    0.00  294.29   86605.10
    batches_consumed_total                  0.00  273.00   54.86    9.00   79.68    6349.05
    batches_delivered                       0.00  274.00   55.43    9.00   97.04    9417.34
    batches_produced_total                  0.00  552.00   87.86   18.00  155.38   24142.75
    batches_received                       18.00  272.00  110.71   99.00   81.08    6573.24
    batches_requested                     274.00  654.00  481.71  451.00  129.85   16860.24
    bootstrap_all_paths_time_sec            0.00    0.00    0.00    0.00    0.00       0.00
    crash_signals_sent                      0.00    0.00    0.00    0.00     NaN        NaN
    empty_inbound_inventory_occurrences     0.00  653.00  240.57  136.50  264.72   70079.03
    empty_outbound_inventory_occurrences    0.00  820.00  184.93    0.00  294.46   86705.46
    failed_flow_queries                     0.00    0.00    0.00    0.00    0.00       0.00
    failed_flow_update                      0.00    0.00    0.00    0.00    0.00       0.00
    flow_queries                          551.00 1487.00  796.57  590.50  338.51  114587.65
    full_flow_bootstrap_time_sec            0.00    0.01    0.00    0.00    0.00       0.00
    heartbeats_sent                       197.00  949.00  578.75  583.50  267.74   71683.93
    inbound_wal_size                        0.00  546.00  111.21   46.00  157.03   24658.95
    nodes_determined_crashed                0.00    0.00    0.00    0.00    0.00       0.00
    op_generator_cycles                   548.00  548.00  548.00  548.00     NaN        NaN
    outbound_material_buildup               0.00  277.00   32.14    0.00   76.03    5780.44
    outbound_wal_size                       0.00  543.00   87.21   18.00  153.32   23505.87
    received_messages                       0.00 3261.00 1253.36 1068.50 1302.85 1697405.17
    recover_signals_sent                    0.00    0.00    0.00    0.00     NaN        NaN
    sent_messages                           0.00 3275.00 1254.71  811.50 1345.46 1810270.84
    skipped_manufacture_cycles              0.00  533.00  225.50  137.00  242.35   58731.19
    successful_manufacture_cycles           0.00  551.00   87.64   18.00  155.05   24041.63
    total_manufacture_cycles              542.00  567.00  556.07  552.50   10.20     104.07
    unanswered_batch_requests_current       0.00    3.00    0.50    0.00    0.94       0.88
    wal_ghost_inbound_batches               0.00    0.00    0.00    0.00    0.00       0.00
    wal_ghost_outbound_batches              0.00    0.00    0.00    0.00    0.00       0.00
    wal_recovered_inbound_batches           0.00    0.00    0.00    0.00    0.00       0.00
    wal_recovered_outbound_batches          0.00    0.00    0.00    0.00    0.00       0.00
    ```

- med-large-no-fail `--num_types 15 --nodes_per_type 2 --failure_rate 0 --recover_rate 0`

    ```csv
                                             min    max   mean median    std      var
    metric_name
    BatchDeliveryConfirmResponse_received   2.00  27.00  12.00   7.00  13.23   175.00
    BatchDeliveryConfirmResponse_sent       1.00  19.00   3.27   1.00   5.62    31.62
    BatchRequest_received                  21.00 139.00  57.86  55.00  30.23   914.13
    BatchRequest_sent                       7.00 134.00  55.43  36.00  44.41  1971.96
    BatchSentResponse_received              1.00  19.00   3.27   1.00   5.62    31.62
    BatchSentResponse_sent                  2.00  27.00  12.00   7.00  13.23   175.00
    BatchUnavailableResponse_received      12.00 143.00  62.11  42.00  45.85  2101.88
    BatchUnavailableResponse_sent          20.00 132.00  58.60  54.50  29.43   866.15
    HeartbeatReq_received                  10.00 167.00  90.95  89.00  39.87  1589.38
    HeartbeatReq_sent                      30.00 141.00  86.82  84.00  30.50   930.44
    HeartbeatResp_received                 29.00 157.00  91.27  89.00  33.25  1105.45
    HeartbeatResp_sent                     10.00 165.00  91.27  89.50  39.89  1590.87
    InformLeaderOfDeathReq_received       216.00 216.00 216.00 216.00    NaN      NaN
    InformLeaderOfDeathReq_sent             1.00  42.00  12.29  11.00   9.85    97.10
    WaitingForBatchResponse_received        2.00  27.00  12.00   7.00  13.23   175.00
    WaitingForBatchResponse_sent            1.00  19.00   3.27   1.00   5.62    31.62
    batch_unavailable_messages_received    12.00 145.00  62.11  42.00  45.72  2090.65
    batch_unavailable_messages_sent         0.00 132.00  41.75  40.50  36.59  1338.64
    batches_consumed_total                  0.00   7.00   0.32   0.00   1.36     1.86
    batches_delivered                       0.00  27.00   1.29   0.00   5.22    27.25
    batches_produced_total                  0.00 513.00  18.64   0.00  96.89  9388.53
    batches_received                        1.00  19.00   3.27   1.00   5.62    31.62
    batches_requested                       7.00 136.00  55.33  37.00  44.77  2004.43
    bootstrap_all_paths_time_sec            0.00   0.02   0.00   0.00   0.00     0.00
    crash_signals_sent                      0.00   0.00   0.00   0.00    NaN      NaN
    empty_inbound_inventory_occurrences     0.00 138.00  42.07  22.00  46.19  2133.18
    empty_outbound_inventory_occurrences    0.00 130.00  41.93  40.50  36.47  1329.70
    failed_flow_queries                     0.00   0.00   0.00   0.00   0.00     0.00
    failed_flow_update                      0.00   0.00   0.00   0.00   0.00     0.00
    flow_queries                          532.00 666.00 572.04 570.00  33.30  1109.00
    full_flow_bootstrap_time_sec            0.00   0.25   0.07   0.04   0.06     0.00
    heartbeats_sent                        30.00 142.00  87.64  85.00  30.93   956.81
    inbound_wal_size                        0.00  27.00   2.57   0.00   7.02    49.22
    nodes_determined_crashed                0.00   0.00   0.00   0.00   0.00     0.00
    op_generator_cycles                   548.00 548.00 548.00 548.00    NaN      NaN
    outbound_material_buildup               0.00 485.00  17.32   0.00  91.66  8400.89
    outbound_wal_size                       0.00 513.00  18.64   0.00  96.89  9388.53
    received_messages                       0.00 524.00 240.54 247.50 166.11 27593.74
    recover_signals_sent                    0.00   0.00   0.00   0.00    NaN      NaN
    sent_messages                           0.00 472.00 230.75 246.00 158.43 25101.53
    skipped_manufacture_cycles              0.00  42.00  13.64  16.00  10.41   108.46
    successful_manufacture_cycles           0.00 513.00  18.64   0.00  96.89  9388.53
    total_manufacture_cycles              510.00 548.00 530.07 530.50  12.50   156.22
    unanswered_batch_requests_current       0.00   0.00   0.00   0.00   0.00     0.00
    wal_ghost_inbound_batches               0.00   0.00   0.00   0.00   0.00     0.00
    wal_ghost_outbound_batches              0.00   0.00   0.00   0.00   0.00     0.00
    wal_recovered_inbound_batches           0.00   0.00   0.00   0.00   0.00     0.00
    wal_recovered_outbound_batches          0.00   0.00   0.00   0.00   0.00     0.00

    ```

- large-no-fail `--num_types 20 --nodes_per_type 2 --failure_rate 0 --recover_rate 0`

    ```csv
                                            min    max   mean median    std      var
    metric_name
    BatchDeliveryConfirmResponse_received   8.00   8.00   8.00   8.00    NaN      NaN
    BatchDeliveryConfirmResponse_sent       1.00   8.00   2.40   1.00   3.13     9.80
    BatchRequest_received                  43.00  98.00  73.37  76.00  18.61   346.36
    BatchRequest_sent                      42.00 253.00 162.79 166.00  70.59  4982.40
    BatchSentResponse_received              1.00   7.00   2.20   1.00   2.68     7.20
    BatchSentResponse_sent                  8.00  45.00  26.50  26.50  26.16   684.50
    BatchUnavailableResponse_received       3.00 149.00  58.12  70.00  43.23  1868.74
    BatchUnavailableResponse_sent          43.00  97.00  74.11  77.00  16.83   283.40
    HeartbeatReq_received                   4.00  75.00  53.75  60.00  17.95   322.30
    HeartbeatReq_sent                      34.00 109.00  57.35  53.50  16.44   270.34
    HeartbeatResp_received                  7.00  97.00  47.55  43.00  17.93   321.63
    HeartbeatResp_sent                      4.00  76.00  53.75  58.50  17.81   317.04
    InformLeaderOfDeathReq_sent             1.00   5.00   2.42   2.00   1.07     1.15
    WaitingForBatchResponse_received        8.00   8.00   8.00   8.00    NaN      NaN
    WaitingForBatchResponse_sent            1.00   8.00   2.40   1.00   3.13     9.80
    batch_unavailable_messages_received     3.00 147.00  57.88  69.00  42.91  1841.24
    batch_unavailable_messages_sent         0.00  98.00  35.05   0.00  39.18  1534.81
    batches_consumed_total                  0.00   8.00   0.21   0.00   1.30     1.68
    batches_delivered                       0.00   8.00   0.21   0.00   1.30     1.68
    batches_produced_total                  0.00  53.00   1.61   0.00   8.66    75.00
    batches_received                        1.00   8.00   2.40   1.00   3.13     9.80
    batches_requested                      41.00 252.00 162.16 164.00  69.70  4858.58
    bootstrap_all_paths_time_sec            0.00   0.37   0.07   0.05   0.08     0.01
    crash_signals_sent                      0.00   0.00   0.00   0.00    NaN      NaN
    empty_inbound_inventory_occurrences     0.00 255.00  81.53  21.00  96.09  9233.34
    empty_outbound_inventory_occurrences    0.00  98.00  35.11   0.00  39.20  1536.85
    failed_flow_queries                   140.00 185.00 150.18 143.50  15.55   241.78
    failed_flow_update                      0.00   0.00   0.00   0.00   0.00     0.00
    flow_queries                          181.00 329.00 235.47 230.00  37.70  1421.45
    full_flow_bootstrap_time_sec          476.74 489.75 482.07 482.13   2.78     7.75
    heartbeats_sent                        34.00 113.00  57.95  53.50  16.91   286.05
    inbound_wal_size                        0.00  45.00   1.71   0.00   7.66    58.75
    nodes_determined_crashed                0.00   0.00   0.00   0.00   0.00     0.00
    op_generator_cycles                   548.00 548.00 548.00 548.00    NaN      NaN
    outbound_material_buildup               0.00   8.00   0.21   0.00   1.30     1.68
    outbound_wal_size                       0.00  53.00   1.61   0.00   8.66    75.00
    received_messages                       0.00 368.00 116.76 124.00 120.06 14414.02
    recover_signals_sent                    0.00   0.00   0.00   0.00    NaN      NaN
    sent_messages                           0.00 454.00 174.55 131.50 181.39 32901.23
    skipped_manufacture_cycles            141.00 238.00 167.79 169.00  24.13   582.28
    successful_manufacture_cycles           0.00  53.00   1.61   0.00   8.66    75.00
    total_manufacture_cycles              165.00 260.00 199.92 193.00  27.99   783.48
    unanswered_batch_requests_current       0.00 188.00  56.29   0.00  67.21  4516.64
    wal_ghost_inbound_batches               0.00   0.00   0.00   0.00   0.00     0.00
    wal_ghost_outbound_batches              0.00   0.00   0.00   0.00   0.00     0.00
    wal_recovered_inbound_batches           0.00   0.00   0.00   0.00   0.00     0.00
    wal_recovered_outbound_batches          0.00   0.00   0.00   0.00   0.00     0.00

    ```

#### Low Failures

- small-low-failure `--num_types 5 --nodes_per_type 2 --failure_rate 1 --recover_rate 1`

    ```csv
                                             min    max   mean median    std      var
    metric_name
    BatchDeliveryConfirmResponse_received   6.00  27.00  13.40   8.00   9.24    85.30
    BatchDeliveryConfirmResponse_sent       7.00  20.00  13.40  15.00   6.11    37.30
    BatchRequest_received                  13.00  84.00  48.60  46.00  29.21   853.30
    BatchRequest_sent                       8.00  84.00  48.80  60.00  32.77  1073.70
    BatchSentResponse_received              7.00  21.00  13.80  15.00   6.14    37.70
    BatchSentResponse_sent                  6.00  29.00  13.80   8.00   9.98    99.70
    BatchUnavailableResponse_received      42.00  69.00  58.33  64.00  14.36   206.33
    BatchUnavailableResponse_sent           5.00  66.00  43.75  52.00  28.41   806.92
    HeartbeatReq_received                  30.00  60.00  49.83  59.50  15.37   236.17
    HeartbeatReq_sent                      30.00  60.00  49.83  59.50  15.37   236.17
    HeartbeatResp_received                 30.00  60.00  50.00  60.00  15.49   240.00
    HeartbeatResp_sent                     30.00  60.00  49.83  59.50  15.37   236.17
    InformLeaderOfDeathReq_received         2.00   2.00   2.00   2.00    NaN      NaN
    InformLeaderOfDeathReq_sent             1.00   1.00   1.00   1.00   0.00     0.00
    WaitingForBatchResponse_received        6.00  29.00  13.80   8.00   9.98    99.70
    WaitingForBatchResponse_sent            7.00  21.00  13.80  15.00   6.14    37.70
    batch_unavailable_messages_received    42.00  69.00  58.33  64.00  14.36   206.33
    batch_unavailable_messages_sent         0.00  66.00  21.88   2.50  29.88   892.70
    batches_consumed_total                  0.00  19.00   8.00   6.50   8.05    64.86
    batches_delivered                       0.00  27.00   8.38   6.50   9.84    96.84
    batches_produced_total                  0.00 558.00  76.88   7.00 194.53 37843.55
    batches_received                        7.00  21.00  13.80  15.00   6.14    37.70
    batches_requested                       8.00  84.00  48.80  60.00  32.77  1073.70
    bootstrap_all_paths_time_sec            0.00   0.00   0.00   0.00   0.00     0.00
    crash_signals_sent                      2.00   2.00   2.00   2.00    NaN      NaN
    empty_inbound_inventory_occurrences     0.00  84.00  30.50  14.50  35.38  1251.43
    empty_outbound_inventory_occurrences    0.00  66.00  21.88   2.50  29.88   892.70
    failed_flow_queries                     0.00   0.00   0.00   0.00   0.00     0.00
    failed_flow_update                      0.00   0.00   0.00   0.00   0.00     0.00
    flow_queries                          536.00 635.00 573.25 572.00  30.96   958.79
    full_flow_bootstrap_time_sec            0.00   0.00   0.00   0.00   0.00     0.00
    heartbeats_sent                        30.00  60.00  49.67  59.00  15.24   232.27
    inbound_wal_size                        0.00  40.00  17.25  14.50  13.91   193.36
    nodes_determined_crashed                0.00   0.00   0.00   0.00   0.00     0.00
    op_generator_cycles                   544.00 544.00 544.00 544.00    NaN      NaN
    outbound_material_buildup               0.00 528.00  68.12   0.00 185.86 34543.55
    outbound_wal_size                       0.00 557.00  76.75   7.00 194.18 37706.21
    received_messages                       0.00 276.00 153.12 174.50 107.44 11543.55
    recover_signals_sent                    2.00   2.00   2.00   2.00    NaN      NaN
    sent_messages                           0.00 277.00 152.88 179.00 114.27 13056.70
    skipped_manufacture_cycles              0.00  71.00  28.88  14.50  32.77  1073.84
    successful_manufacture_cycles           0.00 558.00  76.88   7.00 194.53 37843.55
    total_manufacture_cycles              452.00 573.00 543.75 565.00  45.32  2053.93
    unanswered_batch_requests_current       0.00   0.00   0.00   0.00   0.00     0.00
    wal_ghost_inbound_batches               0.00  19.00   3.12   0.00   6.75    45.55
    wal_ghost_outbound_batches              0.00   0.00   0.00   0.00   0.00     0.00
    wal_recovered_inbound_batches           0.00  20.00   3.50   0.00   7.23    52.29
    wal_recovered_outbound_batches          0.00  19.00   2.75   0.00   6.65    44.21


    ```

- med-low-fail `--num_types 8 --nodes_per_type 2 --failure_rate 1 --recover_rate 1`

    ```csv
                                             min    max   mean median    std      var
    metric_name
    BatchDeliveryConfirmResponse_received   1.00  61.00  20.11  12.00  23.93   572.61
    BatchDeliveryConfirmResponse_sent       1.00  61.00  18.10  14.00  18.53   343.21
    BatchRequest_received                  20.00 189.00  76.10  67.00  52.76  2783.88
    BatchRequest_sent                      13.00 180.00  76.30  77.50  52.22  2726.46
    BatchSentResponse_received              2.00  60.00  18.20  14.00  18.24   332.84
    BatchSentResponse_sent                  1.00  61.00  20.33  12.00  23.84   568.50
    BatchUnavailableResponse_received      10.00 151.00  64.56  53.00  48.22  2325.28
    BatchUnavailableResponse_sent          17.00 128.00  64.33  67.00  40.45  1636.00
    HeartbeatReq_received                  30.00 230.00 101.27 100.00  70.49  4969.22
    HeartbeatReq_sent                      30.00 250.00 111.40 119.50  73.62  5419.82
    HeartbeatResp_received                 27.00 249.00 110.50 119.50  73.80  5446.94
    HeartbeatResp_sent                     30.00 230.00 101.45 100.00  70.59  4982.27
    InformLeaderOfDeathReq_received         5.00   5.00   5.00   5.00    NaN      NaN
    InformLeaderOfDeathReq_sent             1.00   1.00   1.00   1.00   0.00     0.00
    WaitingForBatchResponse_received        1.00  61.00  20.22  12.00  23.85   568.94
    WaitingForBatchResponse_sent            2.00  61.00  18.30  14.00  18.50   342.23
    batch_unavailable_messages_received    10.00 151.00  64.56  53.00  48.22  2325.28
    batch_unavailable_messages_sent         0.00 128.00  41.36  30.00  45.14  2037.48
    batches_consumed_total                  0.00  61.00  12.29   3.50  17.53   307.14
    batches_delivered                       0.00  61.00  12.93   3.50  21.27   452.38
    batches_produced_total                  0.00 552.00  49.36   5.00 145.62 21205.79
    batches_received                        2.00  61.00  18.00  13.50  18.37   337.56
    batches_requested                      12.00 180.00  76.10  77.50  52.48  2754.54
    bootstrap_all_paths_time_sec            0.00   0.00   0.00   0.00   0.00     0.00
    crash_signals_sent                      5.00   5.00   5.00   5.00    NaN      NaN
    empty_inbound_inventory_occurrences     0.00 180.00  54.43  42.50  56.27  3166.26
    empty_outbound_inventory_occurrences    0.00 128.00  41.50  30.50  44.99  2024.27
    failed_flow_queries                     0.00   0.00   0.00   0.00   0.00     0.00
    failed_flow_update                      0.00   0.00   0.00   0.00   0.00     0.00
    flow_queries                          487.00 746.00 590.79 582.50  59.24  3509.26
    full_flow_bootstrap_time_sec            0.00   0.00   0.00   0.00   0.00     0.00
    heartbeats_sent                        30.00 250.00 111.40 120.00  73.50  5402.93
    inbound_wal_size                        0.00 122.00  26.00  12.50  34.08  1161.54
    nodes_determined_crashed                0.00   0.00   0.00   0.00   0.00     0.00
    op_generator_cycles                   588.00 588.00 588.00 588.00    NaN      NaN
    outbound_material_buildup               0.00 490.00  36.43   0.00 130.60 17057.19
    outbound_wal_size                       0.00 552.00  49.50   5.00 145.59 21197.81
    received_messages                       0.00 766.00 293.93 239.50 263.31 69331.15
    recover_signals_sent                    5.00   5.00   5.00   5.00    NaN      NaN
    sent_messages                           0.00 790.00 294.07 185.00 274.60 75406.53
    skipped_manufacture_cycles              0.00 118.00  46.36  40.50  43.99  1935.17
    successful_manufacture_cycles           0.00 552.00  49.43   5.00 145.61 21202.57
    total_manufacture_cycles              452.00 568.00 537.21 559.00  45.74  2092.18
    unanswered_batch_requests_current       0.00   2.00   0.36   0.00   0.63     0.40
    wal_ghost_inbound_batches               0.00  19.00   2.21   0.00   5.22    27.26
    wal_ghost_outbound_batches              0.00   1.00   0.07   0.00   0.27     0.07
    wal_recovered_inbound_batches           0.00  20.00   3.29   0.00   6.34    40.22
    wal_recovered_outbound_batches          0.00  11.00   1.57   0.00   3.25    10.57
    ```

- med-large-low-fail `--num_types 15 --nodes_per_type 2 --failure_rate 1 --recover_rate 1`

    ```csv
                                             min    max   mean median    std      var
    metric_name
    BatchDeliveryConfirmResponse_received   2.00  38.00  16.67  10.00  18.90   357.33
    BatchDeliveryConfirmResponse_sent       1.00  30.00   5.56   2.00   9.42    88.78
    BatchRequest_received                  28.00 164.00  79.52  57.00  48.58  2360.06
    BatchRequest_sent                       8.00 203.00  77.86  48.00  65.93  4346.43
    BatchSentResponse_received              1.00  30.00   5.56   2.00   9.42    88.78
    BatchSentResponse_sent                  2.00  38.00  16.67  10.00  18.90   357.33
    BatchUnavailableResponse_received       9.00 207.00  85.68  58.00  66.95  4482.01
    BatchUnavailableResponse_sent          30.00 163.00  81.90  59.00  48.37  2339.36
    HeartbeatReq_received                  30.00 239.00 132.64 149.50  63.56  4039.67
    HeartbeatReq_sent                      30.00 228.00 127.41 142.50  60.45  3653.87
    HeartbeatResp_received                 30.00 238.00 132.00 150.00  62.82  3945.90
    HeartbeatResp_sent                     30.00 236.00 132.23 149.00  62.96  3963.42
    InformLeaderOfDeathReq_received       336.00 336.00 336.00 336.00    NaN      NaN
    InformLeaderOfDeathReq_sent             1.00  65.00  17.32  14.00  15.21   231.23
    WaitingForBatchResponse_received        2.00  38.00  16.67  10.00  18.90   357.33
    WaitingForBatchResponse_sent            1.00  30.00   5.56   2.00   9.42    88.78
    batch_unavailable_messages_received     9.00 207.00  85.84  58.00  67.32  4532.03
    batch_unavailable_messages_sent         0.00 164.00  58.61  45.50  55.41  3070.32
    batches_consumed_total                  0.00  10.00   0.43   0.00   1.91     3.66
    batches_delivered                       0.00  38.00   1.79   0.00   7.35    54.03
    batches_produced_total                  0.00 507.00  18.54   0.00  95.75  9167.89
    batches_received                        1.00  30.00   5.56   2.00   9.42    88.78
    batches_requested                       8.00 201.00  77.81  49.00  65.95  4349.26
    bootstrap_all_paths_time_sec            0.00   0.02   0.00   0.00   0.00     0.00
    crash_signals_sent                      3.00   3.00   3.00   3.00    NaN      NaN
    empty_inbound_inventory_occurrences     0.00 203.00  58.68  30.50  66.64  4441.12
    empty_outbound_inventory_occurrences    0.00 162.00  58.46  46.00  55.32  3060.70
    failed_flow_queries                     0.00   0.00   0.00   0.00   0.00     0.00
    failed_flow_update                      0.00   0.00   0.00   0.00   0.00     0.00
    flow_queries                          526.00 686.00 582.86 571.50  49.54  2454.05
    full_flow_bootstrap_time_sec            0.00   0.24   0.09   0.08   0.07     0.00
    heartbeats_sent                        30.00 231.00 127.18 141.50  60.64  3677.20
    inbound_wal_size                        0.00  40.00   3.57   0.00  10.20   104.11
    nodes_determined_crashed                0.00   0.00   0.00   0.00   0.00     0.00
    op_generator_cycles                   542.00 542.00 542.00 542.00    NaN      NaN
    outbound_material_buildup               0.00 468.00  16.71   0.00  88.44  7822.29
    outbound_wal_size                       0.00 507.00  18.54   0.00  95.75  9167.89
    received_messages                       0.00 905.00 343.36 260.50 265.95 70731.05
    recover_signals_sent                    3.00   3.00   3.00   3.00    NaN      NaN
    sent_messages                           0.00 688.00 330.82 263.00 250.45 62724.45
    skipped_manufacture_cycles              0.00  58.00  19.71  19.50  16.27   264.80
    successful_manufacture_cycles           0.00 507.00  18.50   0.00  95.75  9168.56
    total_manufacture_cycles              496.00 548.00 524.32 526.50  17.09   291.93
    unanswered_batch_requests_current       0.00   1.00   0.14   0.00   0.36     0.13
    wal_ghost_inbound_batches               0.00   0.00   0.00   0.00   0.00     0.00
    wal_ghost_outbound_batches              0.00   0.00   0.00   0.00   0.00     0.00
    wal_recovered_inbound_batches           0.00   2.00   0.11   0.00   0.42     0.17
    wal_recovered_outbound_batches          0.00   0.00   0.00   0.00   0.00     0.00
    ```

- large-low-fail `--num_types 20 --nodes_per_type 2 --failure_rate 1 --recover_rate 1`

    ```csv
                                                min    max   mean median   std    var
    metric_name
    batch_unavailable_messages_sent        0.00   0.00   0.00   0.00  0.00   0.00
    batches_consumed_total                 0.00   0.00   0.00   0.00  0.00   0.00
    batches_delivered                      0.00   0.00   0.00   0.00  0.00   0.00
    batches_produced_total                 0.00   0.00   0.00   0.00  0.00   0.00
    bootstrap_all_paths_time_sec           0.00   0.40   0.10   0.09  0.09   0.01
    empty_inbound_inventory_occurrences    0.00   0.00   0.00   0.00  0.00   0.00
    empty_outbound_inventory_occurrences   0.00   0.00   0.00   0.00  0.00   0.00
    failed_flow_queries                  288.00 353.00 296.03 293.00 13.68 187.22
    failed_flow_update                     0.00   0.00   0.00   0.00  0.00   0.00
    flow_queries                         288.00 353.00 296.03 293.00 13.68 187.22
    inbound_wal_size                       0.00   0.00   0.00   0.00  0.00   0.00
    nodes_determined_crashed               0.00   0.00   0.00   0.00  0.00   0.00
    outbound_material_buildup              0.00   0.00   0.00   0.00  0.00   0.00
    outbound_wal_size                      0.00   0.00   0.00   0.00  0.00   0.00
    received_messages                      0.00   0.00   0.00   0.00  0.00   0.00
    sent_messages                          0.00   0.00   0.00   0.00  0.00   0.00
    skipped_manufacture_cycles           288.00 353.00 296.03 293.00 13.68 187.22
    successful_manufacture_cycles          0.00   0.00   0.00   0.00  0.00   0.00
    total_manufacture_cycles             289.00 354.00 297.03 294.00 13.68 187.22
    unanswered_batch_requests_current      0.00   0.00   0.00   0.00  0.00   0.00
    wal_ghost_inbound_batches              0.00   0.00   0.00   0.00  0.00   0.00
    wal_ghost_outbound_batches             0.00   0.00   0.00   0.00  0.00   0.00
    wal_recovered_inbound_batches          0.00   0.00   0.00   0.00  0.00   0.00
    wal_recovered_outbound_batches         0.00   0.00   0.00   0.00  0.00   0.00
    ```
