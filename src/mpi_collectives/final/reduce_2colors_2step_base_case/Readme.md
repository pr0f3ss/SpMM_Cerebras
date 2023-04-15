# Reduce

Low depth implementation of reduce. Currently it relies on the fact, that the reduction takes the same number of cycles for each PE and can therefore immidiately start sending wavelets once it finished local reduction. In the example below this means that once PE 3 has reduced all the values received from PE 4 it can immidiately send them to PE 1.

## Example
An example with 5 PEs.
```
     ┌───┐   ┌───┐
     │   │   │   │
┌─┐ ┌▼┐ ┌┴┐ ┌▼┐ ┌┴┐
│0│ │1│ │2│ │3│ │4│
└─┘ └─┘ └─┘ └─┘ └─┘

     ┌───────┐
     │       │
┌─┐ ┌▼┐ ┌─┐ ┌┴┐ ┌─┐
│0│ │1│ │2│ │3│ │4│
└─┘ └─┘ └─┘ └─┘ └─┘


 ┌───┐
 │   │
┌▼┐ ┌┴┐ ┌─┐ ┌─┐ ┌─┐
│0│ │1│ │2│ │3│ │4│
└─┘ └─┘ └─┘ └─┘ └─┘

```