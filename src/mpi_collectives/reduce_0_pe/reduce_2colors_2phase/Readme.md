# 2 Phase Reduce

The implementation has two phases. It first does chain/checkerboard reduce on groups of *step* PEs. Then it performs chain reduce on the remaining PEs. Notice, that if *step = rect_width* we just perform chain reduce.

Notes:
- step has to be \geq 2
- If Nx \leq 6 * rect_width, optimal step parameter is around \sqrt(rect_width)
- If Nx > 6 * rect_width, optimal step parameter is rect_width i.e. just doing chain reduce.

## Example
An example with 9 PEs. And step size = 3.
```
         ┌──────┐      ┌─────┐                   ┌──────┐
         │      │      │     │                   │      │
┌───┐  ┌─▼─┐  ┌─┴─┐  ┌─▼─┐ ┌─┴─┐ ┌───┐  ┌───┐  ┌─▼─┐  ┌─┴─┐
│ 0 │  │ 1 │  │ 2 │  │ 3 │ │ 4 │ │ 5 │  │ 6 │  │ 7 │  │ 8 │
└─▲─┘  └─┬─┘  └───┘  └───┘ └─▲─┘ └─┬─┘  └─▲─┘  └─┬─┘  └───┘
  │      │                   │     │      │      │
  └──────┘                   └─────┘      └──────┘

                        ┌──────────────────┐
                        │                  │
 ┌───┐  ┌───┐  ┌───┐  ┌─▼─┐ ┌───┐ ┌───┐  ┌─┴─┐  ┌───┐  ┌───┐
 │ 0 │  │ 1 │  │ 2 │  │ 3 │ │ 4 │ │ 5 │  │ 6 │  │ 7 │  │ 8 │
 └─▲─┘  └───┘  └───┘  └─┬─┘ └───┘ └───┘  └───┘  └───┘  └───┘
   │                    │
   └────────────────────┘

```