# Inferential Summary [SIMULATION]

N observations: 23,400

## H1 — Global South vs Global North

| term     |   estimate |   std_error |   ci95_low |   ci95_high |   z_value |   p_value |
|:---------|-----------:|------------:|-----------:|------------:|----------:|----------:|
| is_south |    -0.3305 |     29718.3 |   -58247.1 |     58246.4 |        -0 |         1 |

## H2 — Language × geography interactions

| term                              |   estimate |     std_error |      ci95_low |     ci95_high |   z_value |   p_value |
|:----------------------------------|-----------:|--------------:|--------------:|--------------:|----------:|----------:|
| is_south:is_native_int            |     0.5382 | nan           | nan           | nan           |       nan |       nan |
| is_south:joshi_high               |     0.7463 |   3.04492e+12 |  -5.96793e+12 |   5.96793e+12 |         0 |         1 |
| is_native_int:joshi_high          |     0.4649 | nan           | nan           | nan           |       nan |       nan |
| is_south:is_native_int:joshi_high |    -0.5095 | nan           | nan           | nan           |       nan |       nan |

## H3 — Sabiá-3 × Brazil contrasts

| contrast                    |   estimate_pp |   std_error |   ci95_low_pp |   ci95_high_pp |   p_value |   n_comparator |   n_frontier |
|:----------------------------|--------------:|------------:|--------------:|---------------:|----------:|---------------:|-------------:|
| sabia3_vs_frontier_on_BR    |          8.99 |      0.0207 |          4.94 |          13.04 |     0     |            300 |          900 |
| qwen3_32b_vs_frontier_on_BR |          3.27 |      0.0217 |         -0.97 |           7.51 |     0.131 |            300 |          900 |

