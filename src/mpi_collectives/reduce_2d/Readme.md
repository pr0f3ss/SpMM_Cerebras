# Reduce

Low depth implementation of reduce on a 2d grid. Works for arbitrary grid size.

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