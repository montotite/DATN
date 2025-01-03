
var host = 'http://103.176.251.60:32770'
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
    var day = addZero(date.getDate(), 2);
    var month = addZero(date.getMonth() + 1, 2);
    var year = addZero(date.getFullYear(), 4);

    var h = addZero(date.getHours(), 2);
    var m = addZero(date.getMinutes(), 2);
    var s = addZero(date.getSeconds(), 2);
    var ms = addZero(date.getMilliseconds(), 3);
    var time = day + "/" + month + "/" + year + " " + h + ":" + m + ":" + s + ":" + ms;

    var additional_info = {};
    if (element.additional_info) {
        var additional_info = JSON.parse(element.additional_info);
    }

    var description = additional_info.description || ""
    const item = document.createElement('div');
    item.className = "col-lg-3"
    item.innerHTML = `
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">${element.name}</h5>
            <p class="card-text">${description}</p>
            <p class="card-text">Thời gian tạo: ${time}</p>
            <a href="${element.id}" class="card-link">Chi tiết</a>
        </div>
    </div>    
    `
    return item
}

const form_create_device = document.getElementById("form_create_device");
const device_ls = document.getElementById("device_ls");

form_create_device.addEventListener("submit", create_device)
async function create_device(event) {
    const name = document.getElementById("name");
    const description = document.getElementById("description");
    console.log(name.value)

    const rawResponse = await fetch(`${host}/api/device`, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "name": name.value,
            "additional_info": JSON.stringify({ "description": description.value })
        })
    });
    const content = await rawResponse.json();
    const status = await rawResponse.status;
    if (status == 200) {
        const item = add_device_item(content)
        device_ls.appendChild(item)
    }

}
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
    cons_year.innerText = `${data.year.cost} VND`

    cons_total.innerText = `${data.total.cons} kwh`
    cost_total.innerText = `${data.total.cost} VND`


}
function api_summary() {
    fetch(`${host}/api/dashboard/summary`)
        .then(response => response.json())
        .then(data => load_summary(data))
        .catch(error => console.error('Error:', error));
}
api_device_list(page_size, page);
api_summary();

setInterval(api_summary, 5000);