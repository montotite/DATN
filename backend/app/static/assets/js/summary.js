var host = window.location.origin

const cons_today = document.getElementById("cons_today")
const cost_today = document.getElementById("cost_today")


const cons_month = document.getElementById("cons_month")
const cost_month = document.getElementById("cost_month")


const cons_year = document.getElementById("cons_year")
const cost_year = document.getElementById("cost_year")

const cons_total = document.getElementById("cons_total")
const cost_total = document.getElementById("cost_total")

function load_summary(data) {
    cons_today.innerText = `${data.today.cons} kwh`
    cost_today.innerText = `${data.today.cost} VND`

    cons_month.innerText = `${data.month.cons} kwh`
    cost_month.innerText = `${data.month.cost} VND`

    cons_year.innerText = `${data.year.cons} kwh`
    cost_year.innerText = `${data.year.cost} VND`

    cons_total.innerText = `${data.total.cons} kwh`
    cost_total.innerText = `${data.total.cost} VND`


}
function api_summary() {
    fetch(`${host}/api/dashboard/summary`)
        .then(response => response.json())
        .then(data => load_summary(data))
        .catch(error => console.error('Error:', error));
}

api_summary();
setInterval(api_summary, 5000);