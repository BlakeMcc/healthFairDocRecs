var margin = {top: 20, right: 10, bottom: 20, left: 25};
var width = 400 - margin.left - margin.right;
var height = 250 - margin.top - margin.bottom;
var svg = d3.select("#chart")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
var insuranceSvg = d3.select("#insuranceChart")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


(function() {
  var y = d3.scaleLinear().range([height, 0]);
  var x = d3.scaleBand().rangeRound([0, width]).padding(0.1);

  var screenDates = d3.nest()
    .key(function(d) { return d.date; })
    .rollup(function(v) { return d3.sum(v, function(d) { return d.visits; }); })
    .entries(screenData);

  y.domain([0, d3.max(screenDates, function(d) { return d.value; })]);
  x.domain(screenDates.map(function(d) { return d.key; }));

  svg.append("g")
      .attr("class", "axis x")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));

  svg.append("g")
      .attr("class", "axis y")
      .call(d3.axisLeft(y).ticks(5))
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", "0.71em")
      .attr("text-anchor", "end")
      .text("# Visits");

  var dataBars = svg.append("g");
  dataBars.selectAll("rect")
    .data(screenDates).enter()
    .append("rect")
      .attr("fill", "steelblue")
      .attr("x", function(d) { return x(d.key); })
      .attr("y", function(d) { return y(d.value); })
      .attr("width", x.bandwidth())
      .attr("height", function(d) { return height - y(d.value); });

  dataBars.selectAll("text")
    .data(screenDates).enter()
    .append("text")
      .attr("x", function(d) { return x(d.key)+(x.bandwidth()/2); })
      .attr("y", function(d) { return y(d.value)-10; })
      .style("text-anchor", "middle")
      .text(function(d) { return d.value; });

  var insuranceData = d3.nest()
    .key(function(d) { return d.insurance; })
    .rollup(function(v) { return v.length; })
    .entries(screenData);

  y.domain([0, d3.max(insuranceData, function(d) { return d.value; })]);
  x.domain(insuranceData.map(function(d) { return d.key; }));

  insuranceSvg.append("g")
      .attr("class", "axis x")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));

  insuranceSvg.append("g")
      .attr("class", "axis y")
      .call(d3.axisLeft(y).ticks(5))
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", "0.71em")
      .attr("text-anchor", "end")
      .text("# Screens");

  var insDataBars = insuranceSvg.append("g");
  insDataBars.selectAll("rect")
    .data(insuranceData).enter()
    .append("rect")
      .attr("fill", "steelblue")
      .attr("x", function(d) { return x(d.key); })
      .attr("y", function(d) { return y(d.value); })
      .attr("width", x.bandwidth())
      .attr("height", function(d) { return height - y(d.value); });

  insDataBars.selectAll("text")
    .data(insuranceData).enter()
    .append("text")
      .attr("x", function(d) { return x(d.key)+(x.bandwidth()/2); })
      .attr("y", function(d) { return y(d.value)-10; })
      .style("text-anchor", "middle")
      .text(function(d) { return d.value; });
})()
