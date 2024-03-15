var eLinkState = {
    eNormal: 0,
    eError: 1
};

var eNodeType = {
    eGeneric:   "",
    eGuardian:  "GUARDIAN_DEVICE",
    eRKMSGroup: "REMOTE_KEY_GROUP",
    eRKMS:      "REMOTE_KEY_DEVICE",
    eKMESGroup: "KMES_GROUP",
    eKMES:      "KMES_DEVICE",
    eSSPGroup:  "CARDGROUP",
    eSSP:       "CARD",
    eSASGroup:  "SAS_GROUP",
    eSAS:       "SAS_DEVICE" 
};

// The size of the border around the body div.
var WINDOW_BORDER_SIZE = 5;

// The target distance between two nodes.
var LINK_DISTANCE = 100;

// How much the node moves around when resimulated against charge and gravity.
var LINK_FRICTION = 0.7;

// How much nodes repel one another.
var LINK_CHARGE = -2500;

// Node values for animation
var NODE_CIRCLE_TRANSITION_TIME = 1000;
var NODE_CIRCLE_RADIUS = 18;
var NODE_CIRCLE_MAX_RADIUS = 26;
var NODE_CIRCLE_GLOW_OFFSET = 4;

var cachedNodes = [];

var width = 300;
var height = 300;

var color = null
var body = null;

// This element will let us draw our circles and links!
var svg = null;

var currentNode = null;
var currentNodeCallBack = null;

// This is the business end, the d3 directed force graph.
// Performs the simulation.                          
var force = null;

// Listen for resize events on the div wrapping the SVG
function trackParentDivResize(parentDiv) {
    // Track resize events
    function attachResizeListener(elem, callback) {
        var listener = document.createElement('object');
        listener.type = 'text/html';
        listener.data = 'about:blank';

        // Style the listener element to match the parent's size and position
        var stylePosition = 'display: block; top: 0; left: 0;';
        var styleSize = 'height: 100%; width: 100%;';
        var styleBehavior = 'overflow: hidden; pointer-events: none; z-index: -1;';
        listener.setAttribute('style', stylePosition + styleSize + styleBehavior);

        // Hook into the resize event
        listener.onload = function(e) {
            this.contentDocument.defaultView.addEventListener('resize', callback);
        };

        // Attach the listener element to the provided element
        elem.appendChild(listener);
    }

    // Change the width and height when the network graph is resized
    function updateParentDivSize(parentDiv) {
        width = parentDiv.clientWidth;
        height = parentDiv.clientHeight;
    }

    // Initialize the parent div size
    updateParentDivSize(parentDiv);

    // Call the updater every time a resize happens
    attachResizeListener(parentDiv, function() {
        updateParentDivSize(parentDiv);
        resize();
    });
}

// Initialize the graph
function initGraph(nodeCallBack) {
    // Set up the rendering context
    color = d3.scale.category20();
    body = d3.select(".graph_view");
    svg = body.append("svg")
                  .attr("class", "svg-container")
                  .attr("width", width)
                  .attr("height", height)
                  .on("click", hideAllPopupGraphs);

    // Filter used for selection highlights
    svg.append('filter')
        .attr('id', 'blur-filter')
        .attr('filterUnits', 'userSpaceOnUse')
        .append('feGaussianBlur')
        .attr('in', 'SourceGraphic')
        .attr('stdDeviation', 3);

    // This allows us to resize the svg responsively
    trackParentDivResize(body[0][0]);

    // This is the business end, the d3 directed force graph.
    // Performs the simulation.                          
    force = d3.layout.force()
        .linkDistance(LINK_DISTANCE)
        .friction(LINK_FRICTION)
        .size([width, height])
        .charge(function(node) {
            return LINK_CHARGE;
        });

    currentNodeCallBack = nodeCallBack;
}

/**
 * Check if the given node is selected
 * @param {object}  node  The node to check
 * @return {boolean}  True if selected false otherwise
 */
function isNodeSelected(node) {
    return currentNode && node.objectType === currentNode.objectType && node.objectID === currentNode.objectID;
}

/**
 * Check if the given link from the selected node to child nodes
 * @param {object}  link  The link to check
 * @return {boolean}  True if a source node is selected false otherwise
 */
function isLinkSelected(link) {
    return isNodeSelected(link.source);
}

/**
 * Computes visibility for an element
 * @param {boolean}  isVisible  True if the element should be visible
 * @return {string} visible if isVisible is true hidden otherwise
 */
function elementVisibility(isVisible) {
    return isVisible ? 'visible' : 'hidden';
}

/**
 * Computes the visibility function for glow links
 * @param {object}  link  The link to compute visibility for
 * @return {string}  visible if the link is selected hidden otherwise
 */
function glowLinkVisibility(link) {
    return elementVisibility(isLinkSelected(link));
}

/**
 * Checks and corrects x and y values to be within the bounds of the viewport
 * @param {Object}  element  An object with "x" and "y" keys
 */
function checkBounds(element) {
    var edgeMarginPx = 10;

    // Check top and left bounds
    var lowerBound = 0 + NODE_CIRCLE_RADIUS + NODE_CIRCLE_GLOW_OFFSET + edgeMarginPx;
    element.x = element.x < lowerBound ? lowerBound : element.x;
    element.y = element.y < lowerBound ? lowerBound : element.y;

    // Check bottom and right bounds
    var upperWidthBound = width - NODE_CIRCLE_RADIUS - NODE_CIRCLE_GLOW_OFFSET - edgeMarginPx;
    var upperHeightBound = height - NODE_CIRCLE_RADIUS - NODE_CIRCLE_GLOW_OFFSET - edgeMarginPx;
    element.x = element.x > upperWidthBound ? upperWidthBound : element.x;
    element.y = element.y > upperHeightBound ? upperHeightBound : element.y;
}

/**
 * Moves an SVG node to the foreground by moving it
 * to the end of the NodeList of the parent node
 *
 * @param {Element}    node  An SVG element
 */
function moveNodeToForeground(node) {
    var container = node.parentNode;
    container.removeChild(node);
    container.appendChild(node);
}

/**
 * Updates the d3 force graph, clears the svg of all nodes and links, and
 * redraws the entire thing. Only done on node number changes.
 *
 * @param graph A graph with two arrays of nodes and links.
 */
function updateAndRedrawGraph(graph) {

    var root = graph.nodes[0];

    // Put the root node in the middle.
    root.x = width / 2;
    root.y = height / 2;
    root.fixed = true;

    // Remove all nodes and links.
    svg.selectAll('.node-link').remove();
    svg.selectAll(".node").remove();

    // Use the force... graph!
    force
        .nodes(graph.nodes)
        .links(graph.links);

    // Apply the link data from the graph array to these elements.
    var link = svg.selectAll('.node-link').data(graph.links);

    // ... and give them a visual representation with the link class.
    link.enter().append('g')
        .attr("class", "node-link")

    link.append('line')
        .attr('class', 'link')
        .attr("id", function(d){ return 'link_' + d.link_id; })
        .style("stroke", function(d) { return getLinkColorForState(d.state); })
        .style("stroke-width", function(d) { return Math.sqrt(d.value); });

    link.append('line')
        .attr('class', 'link-glow')
        .attr('id', function (linkData) { return 'link-glow-' + linkData.link_id; })
        .attr('visibility', glowLinkVisibility)
        .style('stroke-width', function(linkData) { return Math.sqrt(linkData.value) * 1.1; });

    link.exit().remove();

    // Apply the node data from the graph array to these elements.
    var node = svg.selectAll(".node").data(graph.nodes);

    // Apply the drag behavior to the nodes.
    var drag = force.drag().on('dragstart', function(data) {
        moveNodeToForeground(this);
        setNodeSelection(data);
        d3.event.sourceEvent.stopPropagation();
    });

    // An element named 'g' will transfer all translations done on it to 
    // all of its children. This keeps everything attached in sync. 
    node.enter()
        .append("g")
        .attr("class", "node")
        .call(drag);

    function nodeClicked(data) {
        if (!d3.event.defaultPrevented) {
            moveNodeToForeground(this);
            setNodeSelection(data);
        }
    }

    // This will be the circle that defines this node.
    node.append("circle")
        .attr("class", "node circle")
        .attr("r", NODE_CIRCLE_RADIUS)
        .on("click", nodeClicked)
        .attr('id', function(d){ return 'graphic_' + d.objectType + d.objectID; })
        .style("stroke", function(d) { return getCircleOutlineColorForState(d.status); })
        .data(false);

    // Highlight of circle
    node.append("circle")
        .attr("class", "node circle-glow")
        .attr('r', NODE_CIRCLE_RADIUS + NODE_CIRCLE_GLOW_OFFSET)
        .on("click", nodeClicked)
        .attr('id', function (nodeData) { return 'graphic-glow-' + nodeData.objectType + nodeData.objectID; })
        .attr('visibility', function (nodeData) { return elementVisibility(isNodeSelected(nodeData)); })
        .data(false);

    // Append an image based on the type of node.
    node.append("image")
        .attr("class", "node_image")
        .attr("xlink:href", function(d) { return getImageForNodeType(d.objectType); })
        .attr("x", -11)
        .attr("y", -11)
        .attr("width", "22px")
        .attr("height", "22px")
        .attr("viewBox", "0 0 22 22");

    // This is the name of the node, like serial/IP or group name.
    node.append("text")
        .attr("class", "node name unselectable")
        .attr("dx", 30)
        .attr("dy", ".35em")
        .text(function(d) { return d.name; });
    
    // This is the status of the node, like Communications Error.
    node.append("text")
        .attr("class", "node status unselectable")
        .attr("dx", 30)
        .attr("dy", "1.35em")
        .attr('id', function(d) { return 'status_' + d.objectType + d.objectID; })
        .text(function(d) { return d.status; });

    // Simple HTML hover title.
    node.append("title")
        .text(function(d) { return d.name; });

    node.exit().remove();

    // On each tick, this applies the transformations done in the simulation
    // to the nodes and links.
    force.on("tick", function() {
        // Update the positions of the two endpoints of the link
        var line = link.selectAll('line');
        line.attr("x1", function(d) {
            checkBounds(d.source);
            return d.source.x;
        });
        line.attr("y1", function(d) {
            checkBounds(d.source);
            return d.source.y;
        });
        line.attr("x2", function(d) {
            checkBounds(d.target);
            return d.target.x;
        });
        line.attr("y2", function(d) {
            checkBounds(d.target);
            return d.target.y;
        });

        // Add a glow effect to the link
        link.selectAll('.link-glow').attr('visibility', glowLinkVisibility);

        // Update the position of the node
        node.attr("transform", function(d) {
            checkBounds(d);
            return "translate(" + d.x + "," + d.y + ")";
        });
    });

    // Do some updating we can't do on the first pass.
    updateGraphInternal(graph);

    // Calm down the initial bounciness.
    startAndSimulateInBackground(150);

    d3.select(window).on("resize", resize);
    resize();
}

/**
* Starts the d3 force graph and runs a number of ticks in the background without
* displaying them, to calm down the initial bounciness.
*
* @param tickIterations Iterations to run in the background.
*/
function startAndSimulateInBackground(tickIterations) {
    var alphaThreshold = 0.001;
    force.start();
    var i = 0;
    for (i = tickIterations; i > 0; --i) {

        force.tick();

        if (force.alpha() < alphaThreshold) {
            break;
        }
    }
}

/**
* Called on resizing of the window. Keeps the root node in the middle,
* and adjusts the size of the force graph simulation zone and the svg.
 */
function resize() {
    var root = force.nodes()[0];
    
    if (root) {
        root.px = width / 2;
        root.x = width / 2;
        root.py = height / 2;
        root.y = height / 2;
    }

    svg.attr("width", width).attr("height", height);
    force.size([width, height]).resume();
}

/**
* Updates the graph without drawing it. Meant to replace status text
* on nodes when they change.
*
* @param graph A graph with two arrays of nodes and links.
*/
function updateGraphInternal(graph) {
    graph.nodes.forEach( function(node) {
        var selectedNode = d3.select('#status_' + node.objectType + node.objectID);
        selectedNode.text(node.status);
        
        selectedNode = d3.select('#graphic_' + node.objectType + node.objectID);
        selectedNode.style("stroke", getCircleOutlineColorForState(node.status));

        if (isDeviceNode(node.objectType)) {
            selectedNode = d3.select('#extra_info_inner_' + node.objectType + node.objectID);
            selectedNode.html("TPS: " + node.tps + 
                           "<p>Requests: " + node.requests + 
                           "<p>Errors: " + node.errors);
        }
    });

    graph.links.forEach ( function(link) {
        var selectedLink = d3.select('#link_' + link.link_id);
        selectedLink.style("stroke", getLinkColorForState(link.state));

        var selectedLinkGlow = d3.select('#link-glow-' + link.link_id);
        selectedLinkGlow.attr('visibility', glowLinkVisibility);
    });
}

/**
* Feeds a graph to the d3 force graph object. Makes the decision whether to 
* redraw the entire simulation or just update specific elements.
*
* @param graph A graph with two arrays of nodes and links.
*/
function feedGraph(graph) {

    // Addition of nodes means we have to redraw the graph.
    if (cachedNodes.length != graph.nodes.length) {
        updateAndRedrawGraph(graph);
    } else {
        updateGraphInternal(graph);
    }

    cachedNodes = graph.nodes;

}

function getCachedNodes() {
    return cachedNodes;
}


/**
* Main entry point. Pass in the JSON arrays of nodes and links and d3 will parse them.
*
* @param data JSON string of two arrays- one of nodes, one of links.
*/
function updateNetworkGraph(data, is_json) {
    if (is_json === false)
        json = JSON.parse(data);
    else 
        json = data;

    feedGraph(json);
}

/**
* Gets the color outline of a node depending on its state.
*
* @param sState The state of the node as a string.
*/
function getLinkColorForState(iState) {
    var cColor = "green";
    
    if (iState === eLinkState.eError) {
        cColor = "red";   
    }

    return cColor;
}

/**
* Gets the color outline of a node depending on its state.
*
* @param sState The state of the node as a string.
*/
function getCircleOutlineColorForState(status) {
    var cColor = "green";
    
    if (status !== "Connected (Processing)" && status !== "Running") {
        cColor = "red";   
    }

    return cColor;
}

/**
* Which image represents a certain RK node type?
*
* @param nodeType The type of the node, given by RK and mirrored in this file.
*
* @return The path of the image to use for this node.
*/
function getImageForNodeType(nodeType) {

    var sImage = "/guardian/static/images/generic.svg";

    switch (nodeType) {
        case eNodeType.eGuardian:
            sImage = "/guardian/static/images/guardian.svg";
            break; 
        case eNodeType.eRKMSGroup:
            sImage = "/guardian/static/images/rkms_group.svg";
            break;
        case eNodeType.eRKMS:
            sImage = "/guardian/static/images/rkms_device.svg";
            break;
        case eNodeType.eKMESGroup:
            sImage = "/guardian/static/images/kmes_group.svg";
            break;
        case eNodeType.eKMES:
            sImage = "/guardian/static/images/kmes_device.svg";
            break;
        case eNodeType.eSSPGroup:
            sImage = "/guardian/static/images/ssp_group.svg";
            break;
        case eNodeType.eSSP:
            sImage = "/guardian/static/images/ssp_device.svg";
            break;
        case eNodeType.eSASGroup:
            sImage = "/guardian/static/images/sas_group.svg";
            break;
        case eNodeType.eSAS:
            sImage = "/guardian/static/images/sas_device.svg";
            break;
    }

    return sImage;
}

/**
* Is this node type referring to a device (not a group)?
*
* @param iNodeType Node's type.
*
* @return True if it's a device node type, false otherwise.
*/
function isDeviceNode(iNodeType) {
    return iNodeType === eNodeType.eRKMS ||
           iNodeType === eNodeType.eKMES ||
           iNodeType === eNodeType.eSSP  ||
           iNodeType === eNodeType.eSAS;
}

/**
* When a node is double-clicked, it will spawn an extra information div. 
* Anything you like can appear there.
*
* @param node Which node was clicked?
*/
function setNodeSelection(node) {
    //var selectedNode = d3.select('#extra_info_' + node.objectID);
    //selectedNode.attr("opacity", "0.8")
    //            .attr("pointer-events", "all");

    d3.selectAll(".circle").each(function(currnode) {
        var currgraphic = d3.select('#graphic_' + currnode.objectType + currnode.objectID);
        currgraphic.transition()
            .attr("r", NODE_CIRCLE_RADIUS)
            .duration(NODE_CIRCLE_TRANSITION_TIME);

        var nodeHighlight = d3.select('#graphic-glow-' + currnode.objectType + currnode.objectID);
        nodeHighlight.attr('visibility', elementVisibility(node === currnode))
            .transition()
            .attr('r', NODE_CIRCLE_RADIUS + NODE_CIRCLE_GLOW_OFFSET)
            .duration(NODE_CIRCLE_TRANSITION_TIME);
    });

    var thisgraphic = d3.select('#graphic_' + node.objectType + node.objectID);
    var graphicHighlight = d3.select('#graphic-glow-' + node.objectType + node.objectID);

    currentNode = node;

    if (currentNodeCallBack !== null) {
        currentNodeCallBack(currentNode);
    }

    repeat();
    function repeat() {
        thisgraphic.transition()
            .duration(NODE_CIRCLE_TRANSITION_TIME)
            .attr("r", NODE_CIRCLE_MAX_RADIUS)
            .transition()
            .duration(NODE_CIRCLE_TRANSITION_TIME)
            .attr("r", NODE_CIRCLE_RADIUS)
            .ease("sine")
            .each("end", repeat);

        graphicHighlight.transition()
            .duration(NODE_CIRCLE_TRANSITION_TIME)
            .attr('r', NODE_CIRCLE_MAX_RADIUS + NODE_CIRCLE_GLOW_OFFSET)
            .transition()
            .duration(NODE_CIRCLE_TRANSITION_TIME)
            .attr('r', NODE_CIRCLE_RADIUS + NODE_CIRCLE_GLOW_OFFSET)
            .ease('sine')
            .each('end', repeat);
    }
}

/**
* When you click on the extra information div, it will close for you.
*
* @param node Which node was clicked?
*/
function hidePopupGraph(node) {
    var selectedNode = d3.select('#extra_info_' + node.objectType + node.objectID);
    selectedNode.attr("opacity", "0.0")
                .attr("pointer-events", "none");
}

/**
* When the background svg element is clicked (ie, not any node), all extra
* information divs will be closed as well.
*/
function hideAllPopupGraphs() {
    if (d3.event.target === this) {
        var selectedNode = d3.selectAll('.extra_info'); selectedNode.attr("opacity", "0.0")
                    .attr("pointer-events", "none");
    }
}

