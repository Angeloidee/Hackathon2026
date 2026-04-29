# Evaluación rápida del generador sintético

## Comparación de momentos básicos

| Variable | Media real | Media sintética | Desv. real | Desv. sintética |
| --- | --- | --- | --- | --- |
| m3_to_bill | 21.3240 | 16.5975 | 29.9585 | 25.4980 |
| days_reading | 88.8525 | 89.3990 | 17.2477 | 8.7158 |
| planned_gap_days | -0.0965 | -0.1190 | 0.5560 | 0.6386 |
| is_zero | 0.0785 | 0.0750 | 0.2690 | 0.2634 |

## Correlación real

|                  |   m3_to_bill |   days_reading |   planned_gap_days |   is_zero |
|:-----------------|-------------:|---------------:|-------------------:|----------:|
| m3_to_bill       |       1      |        -0.2143 |             0.0085 |   -0.2077 |
| days_reading     |      -0.2143 |         1      |            -0.0114 |    0.0025 |
| planned_gap_days |       0.0085 |        -0.0114 |             1      |   -0.0028 |
| is_zero          |      -0.2077 |         0.0025 |            -0.0028 |    1      |

## Correlación sintética

|                  |   m3_to_bill |   days_reading |   planned_gap_days |   is_zero |
|:-----------------|-------------:|---------------:|-------------------:|----------:|
| m3_to_bill       |       1      |         0.0888 |             0.0112 |   -0.1854 |
| days_reading     |       0.0888 |         1      |            -0.2939 |    0.0114 |
| planned_gap_days |       0.0112 |        -0.2939 |             1      |    0.0114 |
| is_zero          |      -0.1854 |         0.0114 |             0.0114 |    1      |

