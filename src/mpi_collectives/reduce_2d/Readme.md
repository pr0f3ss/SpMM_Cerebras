# Reduce

Low depth implementation of reduce on a 2d grid. Currently only works when grid side is power of 2.

## Example
An example with 4 PEs.
```
Round 1

 ┌──────┐
 │      │
┌▼┐    ┌┴┐
│0│    │1│
└─┘    └─┘
 ┌──────┐
 │      │
┌▼┐    ┌┴┐
│2│    │3│
└─┘    └─┘

Round 2

  ┌─┐    ┌─┐
┌─►0│    │1│
│ └─┘    └─┘
│
│
│ ┌─┐    ┌─┐
└─┤2│    │3│
  └─┘    └─┘

```