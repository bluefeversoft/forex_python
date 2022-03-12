var drawChart = function(data) {
  var dataTrace = {
    x: data.time,
    close: data.mid_c,
    open: data.mid_o,
    high: data.mid_h,
    low: data.mid_l,
    increasing: {line: {color: '#2EC886' }, fillcolor: '#24A06B'},
    decreasing: {line: {color: '#FF3A4C' }, fillcolor: '#CC2E3C'},
    type: 'candlestick', 
    xaxis: 'x', 
    yaxis: 'y'
  };
  var layout = {
    showlegend: false,
    paper_bgcolor:"#1e1e1e",
    plot_bgcolor:"#1e1e1e",
    margin:{
      l:60,r:10,b:90,t:10
    },
    xaxis: {
      gridcolor:"#1f292f",
      rangeslider: {
       visible: false
     }
    },
    yaxis: {
      gridcolor:"#1f292f",
    },
    autosize: true,
    font: {
      color: '#efefef'
    }
  };
  
  Plotly.newPlot('chartDiv', [dataTrace], layout, {responsive: true});
  Plotly.Plots.resize(document.getElementById('chartDiv'));
}


var app = new Vue({
    el: '#app',
    data: {
      pairName: '',
      message: 'Hello Beer!',
      kpiData: {},
      timer: null,
      showPrices: false,
      priceData: []
    },
    created: function() {
      this.loadData();
    },
    methods: {
        loadData: async function() {
            console.log("Loading data");
            const response = await fetch('/kpi_data', {cache: "no-store"});
            const data = await response.json();
            this.kpiData = data;
            this.timer = setTimeout(this.loadData, 15000);
        },
        applyOnOffClass: function(val) {
          if(val === 0 || val === false) {
            return "";
          } else {
            return 'alert_green';
          }
        },
        applyDirectionClass: function(val) {
          if( val === 0) {
            return "";
          } else if (val === 1) {
            return 'alert_green';
          } else if (val === -1) {
            return 'alert_red';
          }
        },
        loadPrices: async function(pair) {
          this.priceData = []
          const response = await fetch('/price_data/' + pair);
          const data = await response.json();
          this.priceData = data;
          this.showPrices = true;
          drawChart(this.priceData);
        },
        rowSelected: function(pair) {
          clearInterval(this.timer);
          this.loadPrices(pair);
          this.pairName = pair;
        },
        goHome: function() {
          clearInterval(this.timer);
          this.showPrices = false;
          this.loadData();
        }
    }
  })
