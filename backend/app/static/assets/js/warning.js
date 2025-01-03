var host = window.location.origin
var page = 0
var page_size = 5

const alarm_list = document.getElementById("alarm_list")


function addZero(x, n) {
    while (x.toString().length < n) {
        x = "0" + x;
    }
    return x;
}

function add_alarm_item(element) {
    var date = new Date(element.created_time);
    var day = addZero(date.getDate(), 2);
    var month = addZero(date.getMonth() + 1, 2);
    var year = addZero(date.getFullYear(), 4);

    var h = addZero(date.getHours(), 2);
    var m = addZero(date.getMinutes(), 2);
    var s = addZero(date.getSeconds(), 2);
    var ms = addZero(date.getMilliseconds(), 3);
    var time = day + "/" + month + "/" + year + " " + h + ":" + m + ":" + s;

    // var additional_info = {};
    // if (element.additional_info) {
    //     var additional_info = JSON.parse(element.additional_info);
    // }

    // var description = additional_info.description || ""
    console.log(element)

    const item = document.createElement('tr');
    item.innerHTML = `
                        <td>
                            <div class="">
                            <span>${time}</span>
                            </div>
                        </td>
                        <td>
                            <div class="d-flex align-items-center product">
                            <img src="../assets/images/products/warning.jpg" class="img-fluid flex-shrink-0 rounded"
                                width="24" height="24" />
                            <div class="ms-3 product-title">
                                <h6 class="fs-4 mb-0">
                                ${element.name}
                                </h6>
                            </div>
                            </div>
                        </td>
                        <td>
                            <h5 class="mb-0 fs-4">
                            ${element.value.value}<span class="text-muted">/${element.value.setting} Kwh</span>
                            </h5>
                        </td>
                        <td>
                            <span class="badge rounded-pill fs-2 fw-medium bg-secondary-subtle text-secondary">${element.status}</span>
                        </td>
                        <td>
                            <div class="dropdown dropstart">
                            <button type="button" class="btn btn-primary m-1">Xác nhận</button>
                            </div>
                        </td>
                        `
    return item
}

function load_alarm(data) {
    data.data.forEach(element => {
        // console.log(element)
        const item = add_alarm_item(element)
        alarm_list.appendChild(item)
    }
    );
    if (data.has_next) {
        page++
        api_alarm(page_size, page);
    }
}

function api_alarm(page_size, page) {
    fetch(`${host}/api/alarm?page_size=${page_size}&page=${page}`)
        .then(response => response.json())
        .then(data => load_alarm(data))
        .catch(error => console.log('Error:'));
}
api_alarm(page_size, page)