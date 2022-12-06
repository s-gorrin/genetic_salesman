# TOrder
### A genetic algorithm approach to solving the Traveling Salesman Problem
This was created as an assignment for Boston University MET CS 767.

## Cities File
For simplicity, this just uses a distances matrix as a .csv file, where the
first line of the file is a list of cities in order, the first column is the same
list in the same order, and the intersection of each city is the distance from
one to the other. Units don't matter as long as they're all the same, but the
included cities.csv file is in miles.

## How to run
Simply create an object of the `TOrder` class, passing it a cities file, and 
call the `.run()` method with the number of generations.