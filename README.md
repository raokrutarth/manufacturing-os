
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

    ```

- med-low-fail `--num_types 8 --nodes_per_type 2 --failure_rate 1 --recover_rate 1`

    ```csv

    ```
