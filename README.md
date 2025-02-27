# SLC Pathfinder

A Python application to find and visualize the shortest route between street intersections in Salt Lake City.

## Description

SLC Pathfinder is a navigation tool that allows users to find the shortest path between two street intersections in Salt Lake City. The application uses real geographic data, fuzzy string matching for street name identification, and Dijkstra's algorithm for efficient pathfinding. Results are visualized on an interactive web map.

## Features

- **Street Name Matching**: Fuzzy string matching to identify street names even with minor misspellings or variations
- **Intersection Location**: Finds the exact coordinates where two streets intersect
- **Shortest Path Calculation**: Uses Dijkstra's algorithm to find the optimal route between two intersections
- **Interactive Visualization**: Displays the route on an interactive Folium map that opens in your web browser

## Installation

### Prerequisites

- Python 3.7 or higher
- The following Python libraries:
  - geopandas
  - pandas
  - networkx
  - shapely
  - pooch
  - folium
  - thefuzz

### Setup

1. Clone this repository or download the source code
2. Install the required dependencies:

```bash
pip install geopandas pandas networkx shapely pooch folium thefuzz
```

## Usage

Run the script from the command line:

```bash
python3 pathfinder.py
```

When prompted:
1. Enter your starting location as two intersecting streets separated by a comma (e.g., "State Street, 800 South")
2. Enter your destination location in the same format
3. The application will calculate the shortest path and open it in your default web browser

### Example

```
Welcome to SLC Pathfinder!
-------------------------
Enter your starting location (format: street name, street name): State Street, 400 South
Enter your destination (format: street name, street name): 700 East, 900 South

Planning route from State Street & 400 South to 700 East & 900 South...
Path found! Opening map in your browser...
```

## How It Works

1. **Data Acquisition**: The application retrieves Salt Lake City road network data using the pooch library
2. **Street Name Matching**: 
   - Uses fuzzy string matching to find the closest match for user input
   - Handles variations in street naming conventions (e.g., "700 S" vs "700 South")
3. **Intersection Finding**:
   - Identifies all road segments for each street
   - Finds common nodes where the streets intersect
4. **Pathfinding**:
   - Constructs a weighted graph where:
     - Nodes are road intersections
     - Edges are road segments
     - Weights are distances between nodes
   - Applies Dijkstra's algorithm to find the shortest path
5. **Visualization**:
   - Creates an interactive map using Folium
   - Marks the start and end intersections
   - Draws the shortest path route in red

## Limitations

- Works only with Salt Lake City road data
- Requires valid street intersections as input
- Performance may vary with network size
- Some minor streets or new developments may not be included in the dataset

## Future Improvements
- Include information on the path's distance
- Take into account different road types
- Calculate path based on shortest travel time
- Implement alternative routing algorithms
- Include travel time estimation
- Improve error handling and user feedback

## License

This project is available for personal and educational use.
