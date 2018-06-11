# evetools
API wrapper for EVE ESI

eve_primary - Main file with the majority of the functionality

eve_graph - Beginnings of a tool to untilise a graph data structure for route-finding and analyzing Eve system data. The graph holds a representation of the entire Eve k-space universe

# Notes about authentication
- eve_primary relies on OAuth tokens for authentication so you will need to provide that yourself
- An app must be setup on the [EvE Developer Portal](https://developers.eveonline.com/)
- Use a tool such as [postman](https://www.getpostman.com/) to obtain your refresh token
- Supply the values to the variables in the code (and replace them with names meaningful to you
  - replace vars such as avenhor_token with something more general

## Notes about pickled files
- graph.pkl is a pickled dictionary produced when loading the graph and its edge weights
  - load the pickled file to a single dictionary (p_dict for this example)
  - p_dict['graph'] => full graph of systems with edge weights being distance in LY between neighbors
  - p_dict['processed'] => list 'processed_systems' from eve_graph.py of all systems loaded into graph
  - p_dict['edges'] => list 'edges_loaded' from eve_graph.py of edges whose weights have been calculated and added to the graph's nodes
