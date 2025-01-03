const host = window.location.origin
async function event_delete(event) {
    console.log(entity_id.value)
    const rawResponse = await fetch(`${host}/api/device?id=${entity_id.value}`, {
        method: 'DELETE',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    });
    const content = await rawResponse.json();
    const status = await rawResponse.status;
    if (status == 200) {
        location.href = "/devices";
    }
}
function addZero(x, n) {
    while (x.toString().length < n) {
        x = "0" + x;
    }
    return x;
}
function convenTime(created_time) {

    var date = new Date(parseInt(created_time));
    var day = addZero(date.getDate(), 2);
    var month = addZero(date.getMonth() + 1, 2);
    var year = addZero(date.getFullYear(), 4);

    var h = addZero(date.getHours(), 2);
    var m = addZero(date.getMinutes(), 2);
    var s = addZero(date.getSeconds(), 2);
    var ms = addZero(date.getMilliseconds(), 3);
    var time = day + "/" + month + "/" + year + " " + h + ":" + m + ":" + s;
    return time
}


async function get_atribute_api(entity_id) {
    const rawResponse = await fetch(`${host}/api/plugins/telemetry/value/attribute?id=${entity_id}`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    });
    const content = await rawResponse.json();
    const status = await rawResponse.status;
    if (status == 200) {
        return content
    }
    else {
        return false
    }
}





const entity_createtime = document.getElementById("entity_createtime")
const btn_delete = document.getElementById("btn_delete")
const entity_id = document.getElementById("entity_id")
const clinet_scope = document.getElementById("clinet_scope")
const share_scope = document.getElementById("share_scope")
const server_scope = document.getElementById("server_scope")


btn_delete.addEventListener("click", event_delete)
const createtime = entity_createtime.value
entity_createtime.value = convenTime(createtime)

const pathname = window.location.pathname
const pathnames = pathname.split('/')
const entity_id_value = pathnames[pathnames.length - 1];

async function load_telemetry() {
    data = await get_atribute_api(entity_id_value);
    var CLIENT_SCOPE = data.CLIENT_SCOPE
    var SHARED_SCOPE = data.SHARED_SCOPE
    var SERVER_SCOPE = data.SERVER_SCOPE
    if (CLIENT_SCOPE) {
        clinet_scope.innerHTML = ''
        CLIENT_SCOPE.forEach(element => {
            console.log(Object.keys(element)[0])
            const item = document.createElement('tr');
            item.innerHTML = `
            <td>${convenTime(element[Object.keys(element)[0]].ts)}</td>
            <td>${Object.keys(element)[0]}</td>
            <td>${element[Object.keys(element)[0]].value}</td>
            `
            clinet_scope.appendChild(item)
        });
    }
    if (SHARED_SCOPE) {
        share_scope.innerHTML = ''
        SHARED_SCOPE.forEach(element => {
            console.log(Object.keys(element)[0])
            const item = document.createElement('tr');
            item.innerHTML = `
            <td>${convenTime(element[Object.keys(element)[0]].ts)}</td>
            <td>${Object.keys(element)[0]}</td>
            <td>${element[Object.keys(element)[0]].value}</td>
            `
            share_scope.appendChild(item)
        });
    }
    if (SERVER_SCOPE) {
        server_scope.innerHTML = ''
        SERVER_SCOPE.forEach(element => {
            console.log(Object.keys(element)[0])
            const item = document.createElement('tr');
            item.innerHTML = `
            <td>${convenTime(element[Object.keys(element)[0]].ts)}</td>
            <td>${Object.keys(element)[0]}</td>
            <td>${element[Object.keys(element)[0]].value}</td>
            `
            server_scope.appendChild(item)
        });
    }
}

load_telemetry()

setInterval(load_telemetry, 5000);