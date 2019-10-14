
function getData() {
    const JsonElement = $("#graph-data");
    const data = JSON.parse(JsonElement.text());
    return data;
}

function draw_graph(data) {

    container_dims = document.getElementById("graph-container").getBoundingClientRect();
    var width = container_dims.width;
    var height = 600;

    var nodes = data.nodes;
    var links = data.links;

    d3.select('svg')
        .attr('width', width)
        .attr('height', height);

    var simulation = d3.forceSimulation(nodes)
        .force('charge', d3.forceManyBody().strength(-70))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('link', d3.forceLink().links(links).distance(50))
        .on('tick', ticked);

    var div = d3.select("#content").append("div")	
        .attr("class", "tooltip")				
        .style("opacity", 0);

    function updateLinks() {
        var linkContainers = d3.select('.links')
            .selectAll('line')
            .data(links)
        
        linkContainers.enter()
            .append('line')
            .merge(linkContainers)
            .attr('x1', function(d) {
            return d.source.x
            })
            .attr('y1', function(d) {
            return d.source.y
            })
            .attr('x2', function(d) {
            return d.target.x
            })
            .attr('y2', function(d) {
            return d.target.y
            })
        
        linkContainers.exit().remove()
    }

    function updateNodes() {
        nodeContainers = d3.select('.nodes')
          .selectAll('text')
          .data(nodes)
      
        nodeContainers.enter()
            .append('text')
            .text(function(d) { return d.name })
            .merge(nodeContainers)
            .attr('x', function(d) { return d.x })
            .attr('y', function(d) { return d.y })
            .attr('dy', function(d) { return 5 })
            .attr('name', function(d) { return d.name })
            .attr('token', function(d) { return d.token })
            .attr('score', function(d) { return d.score })
            .on("mouseover", function(d) {		
                div.transition()		
                    .duration(200)		
                    .style("opacity", .9);		
                div	.html("name: " + d.name + "<br/>"  + 
                    "token: " + d.token + "<br/>" + 
                    "score: " + ~~(d.score*1000) / 1000)	
                    .style("left", (d3.event.pageX) + "px")		
                    .style("top", (d3.event.pageY - 28) + "px");	
            })					
            .on("mouseout", function(d) {		
                div.transition()		
                    .duration(500)		
                    .style("opacity", 0);	
            });

      
        nodeContainers.exit().remove()
    }

    function ticked() {
        updateNodes()
        updateLinks()
    }

}

$(document).ready(function() {
    var modal = document.getElementById("modal");
    var span = document.getElementsByClassName("close")[0];
    var link = document.getElementById("display-graph");

    link.onclick = function() {
        modal.style.display = "block";
    }
    
    span.onclick = function() {
        modal.style.display = "none";
    }
    
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    draw_graph(getData());
});
