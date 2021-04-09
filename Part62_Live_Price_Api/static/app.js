var app = new Vue({
    el: '#app',
    data: {
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
        },
        rowSelected: function(pair) {
          clearInterval(this.timer);
          this.loadPrices(pair);
        },
        goHome: function() {
          clearInterval(this.timer);
          this.showPrices = false;
          this.loadData();
        }
    }
  })