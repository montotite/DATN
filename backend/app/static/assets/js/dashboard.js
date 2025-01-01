// $(function () {


// =====================================
// Sales Profit Start
// =====================================


var LastYearData = []
var ThisYearData = [
  {
    x: "day 1",
    y: 25,
  },
  {
    x: "day 2",
    y: 25,
  },
  {
    x: "day 3",
    y: 10,
  },
  {
    x: "day 4",
    y: 10,
  },
  {
    x: "day 5",
    y: 45,
  },
  {
    x: "day 6",
    y: 45,
  },
  {
    x: "day 7",
    y: 75,
  },
  {
    x: "day 8",
    y: 70,
  },
  {
    x: "day 9",
    y: 40,
  },
  {
    x: "day 10",
    y: 35,
  },
  {
    x: "day 11",
    y: 35,
  },
  {
    x: "day 12",
    y: 35,
  },
  {
    x: "day 13",
    y: 35,
  },
  {
    x: "day 14",
    y: 35,
  },
  {
    x: "day 15",
    y: 35,
  },
  {
    x: "day 16",
    y: 35,
  },
  {
    x: "day 17",
    y: 35,
  },
  {
    x: "day 19",
    y: 35,
  },
  {
    x: "day 20",
    y: 35,
  },
  {
    x: "day 21",
    y: 35,
  },
  {
    x: "day 22",
    y: 35,
  },
  {
    x: "day 23",
    y: 35,
  },
  {
    x: "day 24",
    y: 35,
  },
  {
    x: "day 25",
    y: 35,
  },
  {
    x: "day 26",
    y: 35,
  },
  {
    x: "day 27",
    y: 35,
  },

  {
    x: "day 28",
    y: 35,
  },
  {
    x: "day 29",
    y: 35,
  },
  {
    x: "day 30",
    y: 35,
  },
]


var options = {
  series: [
    {
      type: "area",
      name: "This Year",
      chart: {
        foreColor: "#111c2d99",
        fontSize: 12,
        fontWeight: 500,
        dropShadow: {
          enabled: true,
          enabledOnSeries: undefined,
          top: 5,
          left: 0,
          blur: 3,
          color: "#000",
          opacity: 0.1,
        },
      },
      data: ThisYearData,
    },
    {
      type: "line",
      name: "Last Year",
      chart: {
        foreColor: "#111c2d99",
      },
      data: [
        {
          x: "day 1",
          y: 100,
        },
        {
          x: "day 2",
          y: 50,
        },
        {
          x: "day 3",
          y: 25,
        },
        {
          x: "day 4",
          y: 20,
        },
        {
          x: "day 5",
          y: 20,
        },
        {
          x: "day 6",
          y: 20,
        },
        {
          x: "day 7",
          y: 35,
        },
        {
          x: "day 9",
          y: 35,
        },
        {
          x: "day 9",
          y: 60,
        },
        {
          x: "day 10",
          y: 40,
        },
        {
          x: "day 11",
          y: 40,
        },
        {
          x: "day 12",
          y: 40,
        },
        {
          x: "day 13",
          y: 40,
        },
        {
          x: "day 14",
          y: 40,
        },
        {
          x: "day 15",
          y: 40,
        },
        {
          x: "day 16",
          y: 40,
        },
        {
          x: "day 17",
          y: 40,
        },
        {
          x: "day 19",
          y: 40,
        },
        {
          x: "day 20",
          y: 40,
        },
        {
          x: "day 21",
          y: 40,
        },
        {
          x: "day 22",
          y: 40,
        },
        {
          x: "day 23",
          y: 40,
        },

        {
          x: "day 24",
          y: 40,
        },
        {
          x: "day 25",
          y: 40,
        },
        {
          x: "day 26",
          y: 40,
        },
        {
          x: "day 27",
          y: 40,
        },
        {
          x: "day 28",
          y: 40,
        },
        {
          x: "day 29",
          y: 40,
        },
        {
          x: "day 30",
          y: 40,
        },
      ],
    },
  ],
  chart: {
    height: 300,
    fontFamily: "inherit",
    foreColor: "#adb0bb",
    fontSize: "12px",
    offsetX: -15,
    offsetY: 10,
    animations: {
      speed: 500,
    },
    toolbar: {
      show: false,
    },
  },
  colors: ["var(--bs-primary)", "var(--bs-secondary-color)"],
  dataLabels: {
    enabled: false,
  },
  fill: {
    type: "gradient",
    gradient: {
      shadeIntensity: 0,
      inverseColors: false,
      opacityFrom: 0.1,
      opacityTo: 0,
      stops: [100],
    },
  },
  grid: {
    show: true,
    strokeDashArray: 3,
    borderColor: "#90A4AE50",
  },
  stroke: {
    curve: "smooth",
    width: 2,
  },
  xaxis: {
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    tickAmount: 3,
  },
  legend: {
    show: false,
  },
  tooltip: {
    theme: "dark",
  },
};
document.getElementById("sales-profit").innerHTML = "";
var chart = new ApexCharts(document.querySelector("#sales-profit"), options);
chart.render();


// })











var host = window.location.origin
// var host = 'http://103.176.251.60:32770'
var page = 0
var page_size = 5

function api_device_list(page_size, page) {
  fetch(`${host}/api/device?page_size=${page_size}&page=${page}`)
    .then(response => response.json())
    .then(data => load_device(data))
    .catch(error => console.error('Error:', error));
}


function addZero(x, n) {
  while (x.toString().length < n) {
    x = "0" + x;
  }
  return x;
}


function add_device_item(element) {
  var date = new Date(element.created_time);
  var day = addZero(date.getDay(), 2);
  var month = addZero(date.getMonth(), 2);
  var year = addZero(date.getFullYear(), 4);

  var h = addZero(date.getHours(), 2);
  var m = addZero(date.getMinutes(), 2);
  var s = addZero(date.getSeconds(), 2);
  var ms = addZero(date.getMilliseconds(), 3);
  var time = day + "/" + month + "/" + year + " " + h + ":" + m + ":" + s;

  var additional_info = {};
  if (element.additional_info) {
    var additional_info = JSON.parse(element.additional_info);
  }

  var description = additional_info.description || ""
  console.log(element.attrbutes.SHARED_SCOPE)
  var status = ""
  if (element.attrbutes.SHARED_SCOPE) {
    if (element.attrbutes.SHARED_SCOPE.value == 'true') {
      var status = "text-warning"
    }
  }
  const item = document.createElement('li');
  item.className = "d-flex align-items-center justify-content-between py-10 border-bottom"
  item.innerHTML = `
  <div class="d-flex align-items-center">
    <div
      class="me-3 rounded-pill d-inline-flex align-items-center justify-content-center">
      <div class="ti ti-brightness-up display-6 ${status}" id="${element.id}"> </div>
    </div>
    <div>
      <h6 class="mb-1 fs-3">${element.name}</h6>
      <p class="mb-0 fs-2 d-flex align-items-center gap-1">
        ${description}<i class="ti ti-info-circle"></i></i>
      </p>
    </div>
  </div>
  
    `
  return item
}

const device_ls = document.getElementById("device_ls");

function load_device(data) {
  data.data.forEach(element => {
    const item = add_device_item(element)
    device_ls.appendChild(item)
  }
  );
  if (data.has_next) {
    page++
    api_device_list(page_size, page);
  }
}

api_device_list(page_size, page);
