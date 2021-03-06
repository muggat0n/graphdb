"""
Pipetypes make up the core functionality of our system.
Once we understand how each one works, we’ll have a better basis for understanding
how they’re invoked and sequenced together in the interpreter.
"""
from functools import partial

from functools import wraps


class GenerativeBase(object):
    def _generate(self):
        s = self.__class__.__new__(self.__class__)
        s.__dict__ = self.__dict__.copy()
        return s


def _generative(func):
    @wraps(func)
    def decorator(self, *args, **kw):
        self = self._generate()
        func(self, *args, **kw)
        return self
    return decorator


class PipeTypes(GenerativeBase):

    """
    Gremlin States:
    done
    pull
    
    """

    def __init__(self, graph):
        self.graph = graph
        # self.pipeTypes = {'_in': partial(self.traversal_in_pipe),
        #                 '_out': partial(self.traversal_out_pipe)}

    def simple_traversal(self, direction):                     # handles basic in and out pipetypes

        if direction == 'out':
            find_method = 'findOutEdges'
            edge_list = '_out'
        else:
            find_method = 'findInEdges'
            edge_list = '_in'

        #@_generative
        def traverse(graph, args, gremlin, state):
            if not gremlin and (not state.edges or not len(state.edges)):         # query initialization
                return 'pull'

            if not state.edges or not len(state.edges):  # state initialization
                state.gremlin = gremlin
                state.edges = graph[find_method](gremlin.vertex).filter(graph.filterEdges(args[0]))

            if not len(state.edges):  # all done
                return 'pull'

            vertex = state.edges.pop()[edge_list]  # use up an edge

            return graph.gotoVertex(state.gremlin, vertex)

        return partial(traverse(graph=self.graph))

    @_generative
    def traversal_in_pipe(self, graph, args, gremlin, state):
        if not gremlin and (not state.edges or not len(state.edges)):
            return 'pull'

        if not state.edges or not len(state.edges):  # state initialization
            state.gremlin = gremlin
            state.edges = graph['findInEdges'](gremlin.vertex).filter(graph.filterEdges(args[0]))

        if not len(state.edges):  # all done
            return 'pull'

        vertex = state.edges.pop()['_in']  # use up an edge

        return graph.gotoVertex(state.gremlin, vertex)

    @_generative
    def traversal_out_pipe(self, graph, args, gremlin, state):
        if not gremlin and (not state.edges or not len(state.edges)):
            return 'pull'

        if not state.edges or not len(state.edges):  # state initialization
            state.gremlin = gremlin
            state.edges = graph['findOutEdges'](gremlin.vertex).filter(graph.filterEdges(args[0]))

        if not len(state.edges):  # all done
            return 'pull'

        vertex = state.edges.pop()['_out']  # use up an edge

        return graph.gotoVertex(state.gremlin, vertex)
    """

        if(!state.edges || !state.edges.length) {                     # state initialization
          state.gremlin = gremlin
          state.edges = graph[find_method](gremlin.vertex)            # get edges that match our query
                             .filter(Dagoba.filterEdges(args[0]))
        }

        if(!state.edges.length)                                       # all done
          return 'pull'

        var vertex = state.edges.pop()[edge_list]                     # use up an edge
        return Dagoba.gotoVertex(state.gremlin, vertex)
      }
    }

    Dagoba.addPipetype('in',  Dagoba.simpleTraversal('in'))
    Dagoba.addPipetype('out', Dagoba.simpleTraversal('out'))
    """
    #Dagoba.Pipetypes = {}                                             # every pipe has a type

    """
    The pipetype’s function is added to the list of pipetypes, and then a new method is added to the query object.
    Every pipetype must have a corresponding query method. That method adds a new step to the query program,
    along with its arguments. When we evaluate the call returns a query object,
    the call adds a new step and returns the query object, and the call does the same.
    This is what enables our method-chaining API.

    Note that adding a new pipetype with the same name replaces the existing one,
    which allows run- time modiﬁcation of existing pipetypes.
    What’s the cost of this decision? What are the alternatives?
    """

    """
    # BUILT-IN PIPE TYPES
    """

    """
    Most pipetypes we meet will take a gremlin and produce more gremlins,
    but this particular pipetype generates gremlins from just a string.
    Given an vertex ID it returns a single new gremlin.
    Given a query it will ﬁnd all matching vertices, and yield one new gremlin at a time until it has worked through them.
    """

    def vertex_pipe(self, graph, args, gremlin, state):
        if not state.vertices:
            state.vertices = graph.findVertices(args)                     # state initialization

        if len(state.vertices) == 0:                                      # all done
            return 'done'

        vertex = state.vertices.pop()                               # OPT: this relies on cloning the vertices
        return graph.makeGremlin(vertex, gremlin.state)                # we can have incoming gremlins from as/back queries



"""
Dagoba.addPipetype('vertex', function(graph, args, gremlin, state) {
  if(!state.vertices)
    state.vertices = graph.findVertices(args)                     # state initialization

  if(!state.vertices.length)                                      # all done
    return 'done'

  var vertex = state.vertices.pop()                               # OPT: this relies on cloning the vertices
  return Dagoba.makeGremlin(vertex, gremlin.state)                # we can have incoming gremlins from as/back queries
})
"""

"""
The function returns a pipetype handler that accepts a gremlin as its input,
and spawns a new gremlin each time it’s queried. Once those gremlins are gone,
it sends back a ‘pull’ request to get a new gremlin from its predecessor.
"""

"""
Dagoba.simpleTraversal = function(dir) {                          # handles basic in and out pipetypes
  var find_method = dir == 'out' ? 'findOutEdges' : 'findInEdges'
  var edge_list   = dir == 'out' ? '_in' : '_out'

  return function(graph, args, gremlin, state) {
    if(!gremlin && (!state.edges || !state.edges.length))         # query initialization
      return 'pull'

    if(!state.edges || !state.edges.length) {                     # state initialization
      state.gremlin = gremlin
      state.edges = graph[find_method](gremlin.vertex)            # get edges that match our query
                         .filter(Dagoba.filterEdges(args[0]))
    }

    if(!state.edges.length)                                       # all done
      return 'pull'

    var vertex = state.edges.pop()[edge_list]                     # use up an edge
    return Dagoba.gotoVertex(state.gremlin, vertex)
  }
}

Dagoba.addPipetype('in',  Dagoba.simpleTraversal('in'))
Dagoba.addPipetype('out', Dagoba.simpleTraversal('out'))
"""


"""
Dagoba.addPipetype('property', function(graph, args, gremlin, state) {
  if(!gremlin) return 'pull'                                      # query initialization
  gremlin.result = gremlin.vertex[args[0]]
  return gremlin.result == null ? false : gremlin                 # undefined or null properties kill the gremlin
})
"""

"""
Dagoba.addPipetype('unique', function(graph, args, gremlin, state) {
  if(!gremlin) return 'pull'                                      # query initialization
  if(state[gremlin.vertex._id]) return 'pull'                     # we've seen this gremlin, so get another instead
  state[gremlin.vertex._id] = true
  return gremlin
})
"""
"""
We’ve seen two simplistic ways of ﬁltering, but sometimes we need more elaborate constraints.
What if we want to ﬁnd all of Thor’s siblings whose weight is greater than their height 22 ?
This query would give us our answer:
"""
"""
Dagoba.addPipetype('filter', function(graph, args, gremlin, state) {
  if(!gremlin) return 'pull'                                      # query initialization

  if(typeof args[0] == 'object')                                  # filter by object
    return Dagoba.objectFilter(gremlin.vertex, args[0])
         ? gremlin : 'pull'

  if(typeof args[0] != 'function') {
    Dagoba.error('Filter arg is not a function: ' + args[0])
    return gremlin                                                # keep things moving
  }

  if(!args[0](gremlin.vertex, gremlin)) return 'pull'             # gremlin fails filter function
  return gremlin
})
"""

"""
We don’t always want all the results at once. Sometimes we only need a handful of results; say we want a dozen of
Thor’s contemporaries, so we walk all the way back to the primeval cow Auumbla:
Without the pipe that query could take quite a while to run, but thanks to our
lazy evaluation strategy the query with the pipe is very e"cient.
Sometimes we just want one at a time: we’ll process the result, work with it,
and then come back for another one. This pipetype allows us to do that as well.
"""

"""
Dagoba.addPipetype('take', function(graph, args, gremlin, state) {
  state.taken = state.taken || 0                                  # state initialization

  if(state.taken == args[0]) {
    state.taken = 0
    return 'done'                                                 # all done
  }

  if(!gremlin) return 'pull'                                      # query initialization
  state.taken++                                                   # THINK: if this didn't mutate state, we could be more
  return gremlin                                                  # cavalier about state management (but run the GC hotter)
})
"""

"""
Dagoba.addPipetype('as', function(graph, args, gremlin, state) {
  if(!gremlin) return 'pull'                                      # query initialization
  gremlin.state.as = gremlin.state.as || {}                       # initialize gremlin's 'as' state
  gremlin.state.as[args[0]] = gremlin.vertex                      # set label to the current vertex
  return gremlin
})
"""

"""
Dagoba.addPipetype('back', function(graph, args, gremlin, state) {
  if(!gremlin) return 'pull'                                      # query initialization
  return Dagoba.gotoVertex(gremlin, gremlin.state.as[args[0]])    # TODO: check for nulls
})
"""

"""
Dagoba.addPipetype('except', function(graph, args, gremlin, state) {
  if(!gremlin) return 'pull'                                      # query initialization
  if(gremlin.vertex == gremlin.state.as[args[0]]) return 'pull'   # TODO: check for nulls
  return gremlin
})
"""

"""
Dagoba.addPipetype('merge', function(graph, args, gremlin, state) {
  if(!state.vertices && !gremlin) return 'pull'                   # query initialization

  if(!state.vertices || !state.vertices.length) {                 # state initialization
    var obj = (gremlin.state||{}).as || {}
    state.vertices = args.map(function(id) {return obj[id]}).filter(Boolean)
  }

  if(!state.vertices.length) return 'pull'                        # done with this batch

  var vertex = state.vertices.pop()
  return Dagoba.makeGremlin(vertex, gremlin.state)
})
"""
