var page = 0
var page_size = 5

function api_device_list(page_size, page) {
    fetch(`http://103.176.251.60:32770/api/device?page_size=${page_size}&page=${page}`)
        .then(response => response.json())
        .then(data => load_device(data))
        .catch(error => console.error('Error:', error));
}

const form_create_device = document.getElementById("form_create_device");
const device_ls = document.getElementById("device_ls");

form_create_device.addEventListener("submit", create_device)
async function create_device(event) {
    const name = document.getElementById("name");
    const description = document.getElementById("description");
    console.log(name.value)

    const rawResponse = await fetch('http://103.176.251.60:32770/api/device', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "name": name.value
        })
    });
    const content = await rawResponse.json();
    console.log(content);
    const item = document.createElement('div');
    item.className = "col-lg-3"
    item.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">${content.name}</h5>
                <p class="card-text">
                Some quick example text to build on the card title and make up
                                        the bulk of
                                        the
                                        card's content.
                </p>
                <a href="#" class="card-link">Chi tiết</a>
            </div>
        </div>    
        `
    device_ls.appendChild(item)
}
function load_device(data) {
    data.data.forEach(element => {
        const item = document.createElement('div');
        item.className = "col-lg-3"
        item.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">${element.name}</h5>
                <p class="card-text">
                Some quick example text to build on the card title and make up
                                        the bulk of
                                        the
                                        card's content.
                </p>
                <a href="#" class="card-link">Chi tiết</a>
            </div>
        </div>    
        `
        device_ls.appendChild(item)
    }
    );
    if (data.has_next) {
        page++
        api_device_list(page_size, page);
    } else {

    }
    console.log();
}
api_device_list(page_size, page);